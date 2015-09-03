'''
Created on Jun 26, 2015

@author: alexandru-m-g
'''

import logging
import mock
import ckan.lib.helpers as h
import ckan.model as model

import ckanext.hdx_theme.tests.hdx_test_base as hdx_test_base
import ckanext.hdx_theme.tests.hdx_test_with_inds_and_orgs as hdx_test_with_inds_and_orgs
import ckanext.hdx_org_group.controllers.custom_org_controller as controller

log = logging.getLogger(__name__)

json_config_wfp = '''
            {
                "visualization-select": "WFP",
                "viz-title": "Test Visualization Title",
                "viz-data-link-url": "https://data.hdx.rwlabs.org/dataset/wfp-food-prices",
                "viz-resource-id": "test-resource-id"
            }
        '''

json_config_3w = '''
        {
            "visualization-select": "3W-dashboard",
            "viz-title": "Who's doing what and where ?",
            "viz-data-link-url": "https://data.hdx.rwlabs.org/dataset/3w-matrix-for-somalia-ngo-consortium",
            "datatype_1": "datastore",
            "dataset_id_1": "dataset_id_1",
            "resource_id_1": "1d5b6821-fe99-4a5d-a0cf-d6987868027b",
            "datatype_2": "filestore",
            "dataset_id_2": "json-repository",
            "resource_id_2": "07c835cd-7b47-4d76-97e0-ff0fd5cc09c5",
            "map_district_name_column": "DIST_NAME",
            "where-column": "DIST_NO",
            "where-column-2": "DIS_CODE",
            "who-column": "Organisation",
            "what-column": "Sector",
            "colors": ["red", "green", "blue"]
        }
        '''

top_line_items = [
    {
        'code': 'test_top_line_code',
        'title': 'Test top line code',
        'source_link': 'http://www.test.test',
        'notes': 'Test top line notes',
        'value': 34567891.2,
        'source': 'Test spirce',
        'explore': '',
        'latest_date': '2015-06-01T00:00:00',
        'units': 'dollars_million',
        '_id': 1
    }
]


class TestMembersController(hdx_test_with_inds_and_orgs.HDXWithIndsAndOrgsTest):

    @classmethod
    def _load_plugins(cls):
        hdx_test_base.load_plugin('hdx_org_group hdx_package hdx_theme')

    @classmethod
    def _create_test_data(cls):
        super(TestMembersController, cls)._create_test_data(create_datasets=True, create_members=True)

    def test_assemble_viz_config(self):
        custom_org_controller = controller.CustomOrgController()

        # Testing the WFP viz part
        config = custom_org_controller.assemble_viz_config(json_config_wfp)

        assert config == {
            'title': 'Test Visualization Title',
            'data_link_url': 'https://data.hdx.rwlabs.org/dataset/wfp-food-prices',
            'type': 'WFP',
            'embedded': 'true',
            # 'resource_id': 'test-resource-id',
            'datastore_id': 'test-resource-id'
        }

        # Testing the 3W viz part
        config = custom_org_controller.assemble_viz_config(json_config_3w)

        assert config, 'Config dict should not be empty'
        assert config == {
            'type': '3W-dashboard',
            'title': "Who's doing what and where ?",
            'geotype': 'filestore',
            'geo': '/dataset/json-repository/resource_download/07c835cd-7b47-4d76-97e0-ff0fd5cc09c5',
            'data_link_url': 'https://data.hdx.rwlabs.org/dataset/3w-matrix-for-somalia-ngo-consortium',
            'data': '/api/action/datastore_search?resource_id=1d5b6821-fe99-4a5d-a0cf-d6987868027b&limit=10000000',
            'datatype': 'datastore',
            'joinAttribute': 'DIS_CODE',
            'whereFieldName': 'DIST_NO',
            'whoFieldName': 'Organisation',
            'whatFieldName': 'Sector',
            'nameAttribute': 'DIST_NAME',
            'colors': ["red", "green", "blue"]
        }

    @mock.patch('ckanext.hdx_crisis.dao.data_access.DataAccess')
    @mock.patch('ckanext.hdx_org_group.controllers.custom_org_controller.request')
    @mock.patch('ckanext.hdx_org_group.controllers.custom_org_controller.c')
    @mock.patch('ckan.lib.helpers.c')
    def test_generate_template_data(self, helper_c_mock, controller_c_mock, req_mock, data_access_cls):
        def mock_get_top_line_items():
            return top_line_items

        data_access_cls.return_value.get_top_line_items.side_effect = mock_get_top_line_items
        req_mock.params = {}
        controller_c_mock.user = 'testsysadmin'
        custom_org_controller = controller.CustomOrgController()
        org_info = {
            'display_name': 'HDX Test Org',
            'name': 'hdx-test-org',
            'id': 'hdx-test-org',
            'visualization_config': json_config_wfp,
            'topline_resource': 'test-topline-resource'
        }

        template_data = custom_org_controller.generate_template_data(org_info)

        assert 'data' in template_data and 'top_line_items' in template_data['data']

        top_lines = template_data['data']['top_line_items']
        assert len(top_lines) == 1

        assert top_lines[0]['latest_date'] == 'Jun 01, 2015'
        assert top_lines[0]['formatted_value'] == '34.6'

        assert 'member_count' in template_data['data']
        assert template_data['data']['member_count'] == 4

    def test_edit_custom_orgs(self):
        url = h.url_for(
            controller='ckanext.hdx_org_group.controllers.organization_controller:HDXOrganizationController', action='edit', id='hdx-test-org')
        testsysadmin = model.User.by_name('testsysadmin')
        result = self.app.get(url, extra_environ={'Authorization': str(testsysadmin.apikey)})
        assert 'id="customization-trigger"' in str(result.response)

        testadmin = model.User.by_name('janedoe3')
        result = self.app.get(url, extra_environ={'Authorization': str(testadmin.apikey)})
        assert 'id="customization-trigger"' not in str(result.response)
