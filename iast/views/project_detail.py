#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# software: PyCharm
# project: lingzhi-webapi

from dongtai.endpoint import R
from dongtai.endpoint import UserEndPoint
from dongtai.models.agent import IastAgent
from dongtai.models.project import (IastProject, VulValidation)
from dongtai.utils.systemsettings import get_vul_validate
from dongtai.utils import const
from django.utils.translation import gettext_lazy as _

from iast.base.project_version import get_project_version, ProjectsVersionDataSerializer
from iast.utils import extend_schema_with_envcheck, get_response_serializer
from rest_framework import serializers


class ProjectsResponseDataSerializer(serializers.Serializer):
    name = serializers.CharField(help_text=_('The name of project'))
    agent_ids = serializers.CharField(help_text=_(
        'The id corresponding to the agent, use, for segmentation.'))
    mode = serializers.ChoiceField(['插桩模式'],
                                   help_text=_('The mode of project'))
    scan_id = serializers.IntegerField(
        help_text=_("The id corresponding to the scanning strategy."))
    versionData = ProjectsVersionDataSerializer(
        help_text=_('Version information about the project'))
    id = serializers.IntegerField(help_text=_("The id of the project"))
    vul_validation = serializers.IntegerField(help_text="vul validation switch")


_ResponseSerializer = get_response_serializer(
    ProjectsResponseDataSerializer(help_text=''),
    status_msg_keypair=(
        ((201, _('success')), ''),
        ((203, _('no permission')), ''),
    ))


class ProjectDetail(UserEndPoint):
    name = "api-v1-project-<id>"
    description = _("View item details")

    @extend_schema_with_envcheck(
        tags=[_('Project')],
        summary=_('Projects Detail'),
        description=
        _("Get project information by project id, including the current version information of the project."
          ),
        response_schema=_ResponseSerializer,
    )
    def get(self, request, id):
        auth_users = self.get_auth_users(request.user)
        project = IastProject.objects.filter(user__in=auth_users, id=id).first()

        if project:
            relations = IastAgent.objects.filter(bind_project_id=project.id, online=const.RUNNING)
            agents = [{"id": relation.id, "name": relation.token} for relation in relations]
            if project.scan:
                scan_id = project.scan.id
                scan_name = project.scan.name
            else:
                scan_id = 0
                scan_name = ''                

            current_project_version = get_project_version(project.id, auth_users)
            return R.success(data={
                "name": project.name,
                "id": project.id,
                "mode": project.mode,
                "scan_id": scan_id,
                "scan_name": scan_name,
                "agents": agents,
                "versionData": current_project_version,
                "vul_validation": project.vul_validation,
                'base_url':project.base_url,
                "test_req_header_key":project.test_req_header_key,
                "test_req_header_value":project.test_req_header_value,
            })
        else:
            return R.failure(status=203, msg=_('no permission'))

