#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# software: PyCharm
# project: lingzhi-webapi
import logging

from dongtai.endpoint import UserEndPoint, R
from dongtai.models.hook_strategy import HookStrategy
from dongtai.utils import const
from django.utils.translation import gettext_lazy as _
from iast.utils import extend_schema_with_envcheck, get_response_serializer
from rest_framework import serializers

logger = logging.getLogger('dongtai-webapi')

OP_CHOICES = ('enable', 'disable', 'delete')
#SCOPE_CHOICES = ('all',)

class EngineHookRuleStatusGetQuerySerializer(serializers.Serializer):
    rule_id = serializers.IntegerField(help_text=_("The id of hook rule"))
    #    rule_type = serializers.IntegerField(help_text=_("The id of hook rule type"))
    op = serializers.ChoiceField(OP_CHOICES,
                                 help_text=_("The state of the hook rule"))
#    scope = serializers.ChoiceField(SCOPE_CHOICES,
#                                 help_text=_("The scope of the hook rule"))


class EngineHookRuleStatusPostBodySerializer(serializers.Serializer):
    ids = serializers.CharField(help_text=_(
        'The id corresponding to the hook type, use"," for segmentation.'))
    op = serializers.ChoiceField(OP_CHOICES,
                                 help_text=_("The state of the hook rule"))


_GetResponseSerializer = get_response_serializer(status_msg_keypair=(
    ((201, _('Operation success')), ''),
    ((202, _('Operation type does not exist')), ''),
    ((202, _('Strategy does not exist')), ''),
))

_PostResponseSerializer = get_response_serializer(status_msg_keypair=(
    ((201, _('Operation success')), ''),
    ((202, _('Operation type does not exist')), ''),
    ((202, _('Incorrect parameter')), ''),
))

class EngineHookRuleEnableEndPoint(UserEndPoint):
    def parse_args(self, request):
        rule_id = request.query_params.get('rule_id')
        rule_type = request.query_params.get('type')
        scope = request.query_params.get('scope')
        op = request.query_params.get('op')
        return rule_id, rule_type, scope, op

    @staticmethod
    def set_strategy_status(strategy_id, strategy_ids, user_id, enable_status):
        if strategy_id:
            rule = HookStrategy.objects.filter(id=strategy_id, created_by=user_id).first()
            if rule:
                rule.enable = enable_status
                rule.save()
                return 1
        elif strategy_ids:
            count = HookStrategy.objects.filter(id__in=strategy_ids, created_by=user_id).update(enable=enable_status)
            return count
        return 0

    @staticmethod
    def check_op(op):
        if op == 'enable':
            op = const.ENABLE
        elif op == 'disable':
            op = const.DISABLE
        elif op == 'delete':
            op = const.DELETE
        else:
            op = None
        return op

    @extend_schema_with_envcheck(
        [EngineHookRuleStatusGetQuerySerializer],
        tags=[_('Hook Rule')],
        summary=_('Hook Rule Status Modify'),
        description=_("Modify the status of the rule corresponding to the specified id."),
        response_schema=_GetResponseSerializer,
    )
    def get(self, request):
        rule_id, rule_type, scope, op = self.parse_args(request)
        try:
            rule_id = int(rule_id)
        except:
            return R.failure(_("Parameter error"))
        user_id = request.user.id
        status = False

        op = self.check_op(op)
        if op is None:
            return R.failure(msg=_('Operation type does not exist'))

        if rule_type is not None and scope == 'all':
            count = HookStrategy.objects.filter(type__id=rule_type, created_by=user_id).update(enable=op)
            logger.info(_('Policy type {} operation success, total of {} Policy types').format(rule_type, count))
            status = True
        elif rule_id is not None:
            status = self.set_strategy_status(strategy_id=rule_id, strategy_ids=None, user_id=user_id,
                                              enable_status=op)
            logger.info(_('Policy {} succeed').format(rule_id))

        if status:
            return R.success(msg=_('Operation success'))
        else:
            return R.failure(msg=_('Strategy does not exist'))

    @extend_schema_with_envcheck(
        request=EngineHookRuleStatusPostBodySerializer,
        tags=[_('Hook Rule')],
        summary=_('Hook Rule Status Modify (Batch)'),
        description=_("Batch modify the status of the rule corresponding to the specified id"),
        response_schema=_PostResponseSerializer,
    )
    def post(self, request):
        op = request.data.get('op')
        op = self.check_op(op)
        if op is None:
            return R.failure(msg=_('Operation type does not exist'))

        strategy_ids = request.data.get('ids')
        try:
            strategy_ids = [int(i) for i in strategy_ids.split(',')]
        except:
            return R.failure(_("Parameter error"))
        if strategy_ids:
            count = self.set_strategy_status(strategy_id=None, strategy_ids=strategy_ids, user_id=request.user.id,
                                             enable_status=op)
            logger.info(_('Strategy operation success, total {}').format(count))
            return R.success(msg=_('Operation success'))
        else:
            return R.failure(msg=_('Incorrect parameter'))
