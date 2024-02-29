from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import job_pb2, job_pb2_grpc
from spaceone.identity.service.job_service import JobService


class Job(BaseAPI, job_pb2_grpc.JobServicer):
    pb2 = job_pb2
    pb2_grpc = job_pb2_grpc

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = JobService(metadata)
        project_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        job_svc = JobService(metadata)
        response: dict = job_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        job_svc = JobService(metadata)
        response: dict = job_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        job_svc = JobService(metadata)
        response: dict = job_svc.stat(params)
        return self.dict_to_message(response)
