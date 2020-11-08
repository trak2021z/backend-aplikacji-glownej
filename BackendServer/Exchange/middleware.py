import os

from django.db import transaction
from django.utils import timezone
from silk.collector import DataCollector
from silk.middleware import SilkyMiddleware
from silk.model_factory import ResponseModelFactory
from silk.profiling.profiler import silk_meta_profiler
import psutil
from django.core.cache import cache, caches
from pymemcache.client import base
import json
from datetime import datetime
import socket


class ProfilerMiddleware(SilkyMiddleware):
    def __call__(self, request):
        if "OBCIAZNIK" in request.headers:
            self.process_request(request)
            response = self.get_response(request)
            response = self.process_response(request, response)
            response['cpu_usage_current'] = json.dumps({'usage': psutil.cpu_percent(), 'timestamp': datetime.now()}, default=str)
            times = psutil.cpu_times()
            response['cpu_time_spent_user'] = times.user
            response['cpu_time_spent_system'] = times.system
            response['cpu_time_spent_idle'] = times.idle
            response['memory_usage'] = psutil.virtual_memory()[2]
            response['container_id'] = socket.gethostname()
            if os.getenv('RUN_MEMCACHE'):
                if os.getenv('RUN_MEMCACHE') == 'TRUE':
                    client = base.Client(('localhost', 11211))
                    response['memory_usage_aggregated'] = client.get('CPU_USAGE')
            return response
        else:
            return self.get_response(request)

    @transaction.atomic()
    def _process_response(self, request, response):
        with silk_meta_profiler():
            collector = DataCollector()
            collector.stop_python_profiler()
            silk_request = collector.request
            if silk_request:
                silk_request.end_time = timezone.now()
                collector.finalise()
                if response.accepted_media_type == 'application/json':
                    response['num_sql_queries'] = silk_request.num_sql_queries
                    response['time_spent_on_sql_queries'] = silk_request.time_spent_on_sql_queries
                    response['time_taken'] = silk_request.time_taken

