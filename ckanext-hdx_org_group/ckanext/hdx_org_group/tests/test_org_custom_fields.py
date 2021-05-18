'''
Created on May 18, 2020

@author: dan mihaila
'''

import logging as logging
import ckan.model as model
import ckan.tests.legacy as tests
import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk

import ckanext.hdx_theme.tests.hdx_test_base as hdx_test_base
import ckanext.hdx_org_group.tests as org_group_base

log = logging.getLogger(__name__)

from ckanext.hdx_org_group.helpers.static_lists import ORGANIZATION_TYPE_LIST



class TestOrgFTSIDAPI(org_group_base.OrgGroupBaseTest):

    @classmethod
    def _load_plugins(cls):
        hdx_test_base.load_plugin('ytp_request hdx_org_group hdx_theme')

    @classmethod
    def _get_action(cls, action_name):
        return tk.get_action(action_name)

    def test_create_org(self):
        context_usr = {'model': model, 'session': model.Session, 'user': 'tester', 'allow_partial_update': True}
        context_sysadmin = {'model': model, 'session': model.Session, 'user': 'testsysadmin'}
        new_org_dict = {
            'name': 'test_org_d',
            'title': 'Test Org D',
            'fts_id': '123456',
            'org_url': 'www.exampleorganization.org',
            'description': 'just a simple description',
            'hdx_org_type': ORGANIZATION_TYPE_LIST[0][1]
        }
        try:
            org_dict = self._get_action('organization_create')(context_sysadmin, new_org_dict)
            assert 'fts_id' in org_dict
            assert org_dict.get('fts_id') == '123456'
        except Exception as ex:
            assert False

        try:
            _org_update_dict = {
                'id': org_dict.get('id'),
                'name': org_dict.get('name'),
                'title': org_dict.get('title'),
                'fts_id': '1234567',
                'org_url': org_dict.get('org_url'),
                'description': org_dict.get('description'),
                'hdx_org_type': org_dict.get('hdx_org_type'),
            }
            self._get_action('organization_update')(context_sysadmin, _org_update_dict)
            org_updated_dict = self._get_action('organization_show')(context_sysadmin, {'id': org_dict.get('id')})
            assert 'fts_id' in org_updated_dict
            assert org_updated_dict.get('fts_id') == '1234567'
        except Exception as ex:
            assert False

        try:
            member_dict = {'id': org_dict.get('id'), 'username': 'tester', 'role': 'admin'}
            self._get_action('organization_member_create')(context_sysadmin, member_dict)
            _org_dict = self._get_action('organization_show')(context_sysadmin, {'id': org_dict.get('id')})
            assert True
        except Exception as ex:
            assert False

        try:
            _org_update_dict = {
                'id': org_updated_dict.get('id'),
                'name': org_updated_dict.get('name'),
                'title': org_updated_dict.get('title'),
                'org_url': org_updated_dict.get('org_url'),
                'description': org_updated_dict.get('description'),
                'hdx_org_type': org_updated_dict.get('hdx_org_type'),
            }
            self._get_action('organization_update')(context_usr, _org_update_dict)
            org_updated_dict = self._get_action('organization_show')(context_sysadmin, {'id': org_dict.get('id')})
            assert 'fts_id' in org_updated_dict
            assert org_updated_dict.get('fts_id') == '1234567'
        except Exception as ex:
            assert False

        try:
            _org_update_dict = {
                'id': org_dict.get('id'),
                'name': org_dict.get('name'),
                'fts_id': '12345678',
                'title': org_dict.get('title'),
                'org_url': org_dict.get('org_url'),
                'description': org_dict.get('description'),
                'hdx_org_type': org_dict.get('hdx_org_type'),
            }
            self._get_action('organization_update')(context_usr, _org_update_dict)
            org_updated_dict = self._get_action('organization_show')(context_sysadmin, {'id': org_dict.get('id')})
            assert 'fts_id' in org_updated_dict
            assert org_updated_dict.get('fts_id') == '1234567'
        except Exception as ex:
            assert False

        assert True


class TestOrgFTSIDController(org_group_base.OrgGroupBaseTest):

    @classmethod
    def _load_plugins(cls):
        hdx_test_base.load_plugin('ytp_request hdx_org_group hdx_theme')

    @classmethod
    def _get_action(cls, action_name):
        return tk.get_action(action_name)

    def test_onboarding(self):
        context_usr = {'model': model, 'session': model.Session, 'user': 'tester', 'allow_partial_update': True}
        context_sysadmin = {'model': model, 'session': model.Session, 'user': 'testsysadmin'}
        testsysadmin = model.User.by_name('testsysadmin')
        sysadmin_auth = {'Authorization': str(testsysadmin.apikey)}
        tester = model.User.by_name('tester')
        tester_auth = {'Authorization': str(tester.apikey)}
        test_client = self.get_backwards_compatible_test_client()

        new_org_url = h.url_for(
            controller='ckanext.hdx_org_group.controllers.organization_controller:HDXOrganizationController',
            action='new')
        new_org_params = {
            'name': 'test_org_d',
            'title': 'Test Org D',
            'fts_id': '123456',
            'org_url': 'www.exampleorganization.org',
            'description': 'just a simple description',
            'hdx_org_type': ORGANIZATION_TYPE_LIST[0][1],
            'save': 'save'
        }
        try:
            result = test_client.post(new_org_url, data=new_org_params, extra_environ=sysadmin_auth)
            org_dict = self._get_action('organization_show')(context_sysadmin, {'id': 'test_org_d'})
            assert '123456' == org_dict.get('fts_id')
            assert '302 Found' in result.body
        except Exception as ex:
            assert False

        try:
            member_dict = {'id': org_dict.get('id'), 'username': 'tester', 'role': 'admin'}
            self._get_action('organization_member_create')(context_sysadmin, member_dict)
            org_dict = self._get_action('organization_show')(context_sysadmin, {'id': org_dict.get('id')})
            assert True
        except Exception as ex:
            assert False

        edit_org_url = h.url_for(
            controller='ckanext.hdx_org_group.controllers.organization_controller:HDXOrganizationController',
            action='edit', id=org_dict.get('id'))
        edit_org_params = {
            'id': org_dict.get('id'),
            'name': 'test_org_d',
            'title': 'Test Org E',
            'org_url': 'www.exampleorganization.org',
            'description': 'just a simple description',
            'hdx_org_type': ORGANIZATION_TYPE_LIST[0][1],
            'save': 'save'
        }
        try:
            result = test_client.post(edit_org_url, data=edit_org_params, extra_environ=tester_auth)
            org_dict = self._get_action('organization_show')(context_sysadmin, {'id': 'test_org_d'})
            assert '123456' == org_dict.get('fts_id')
            assert 'Test Org E' == org_dict.get('title')
        except Exception as ex:
            assert False

        edit_org_params = {
            'id': org_dict.get('id'),
            'name': 'test_org_d',
            'title': 'Test Org E',
            'fts_id': '789',
            'org_url': 'www.exampleorganization.org',
            'description': 'just a simple description',
            'hdx_org_type': ORGANIZATION_TYPE_LIST[0][1],
            'save': 'save'
        }
        try:
            result = test_client.post(edit_org_url, data=edit_org_params, extra_environ=tester_auth)
            org_dict = self._get_action('organization_show')(context_sysadmin, {'id': 'test_org_d'})
            assert '123456' == org_dict.get('fts_id')
            assert 'Test Org E' == org_dict.get('title')
        except Exception as ex:
            assert False
        assert True
