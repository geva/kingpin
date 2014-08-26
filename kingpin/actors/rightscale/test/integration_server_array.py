"""Simple integration tests for the RightScale Server_Array actors."""

from nose.plugins.attrib import attr
import uuid

from tornado import testing

from kingpin.actors import exceptions
from kingpin.actors.rightscale import api
from kingpin.actors.rightscale import server_array


__author__ = 'Matt Wise <matt@nextdoor.com>'


# Generate a common UUID for this particular set of tests
UUID = uuid.uuid4().hex


class IntegrationServerArray(testing.AsyncTestCase):

    """High level RightScale Server Array Actors Testing.

    These tests rely on you having a ServerArray in RightScale named
      'kingpin-integration-testing'
    that can be cloned, launched, terminated, etc.

    Note, these tests must be run in-order. The order is defined by
    their definition order in this file. Nose follows this order according
    to its documentation:

        http://nose.readthedocs.org/en/latest/writing_tests.html


    NOTE: At this point, you need to self-clean-up after yourself
          once you've run these tests. Future tests and features will
          allow for these tests to self-clean-up.
    """

    integration = True

    def setUp(self, *args, **kwargs):
        super(IntegrationServerArray, self).setUp(*args, **kwargs)
        self.template_array = 'kingpin-integration-testing'
        self.template_script = 'kingpin-integration-testing-script'
        self.clone_name = 'kingpin-%s' % UUID

    @attr('integration')
    @testing.gen_test(timeout=60)
    def integration_01a_clone_dry(self):
        actor = server_array.Clone(
            'Clone %s' % self.template_array,
            {'source': self.template_array,
             'dest': self.clone_name},
            dry=True)
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=60)
    def integration_01b_clone_dry_with_missing_template(self):
        actor = server_array.Clone(
            'Clone %s' % self.template_array,
            {'source': 'unit-test-fake-array',
             'dest': self.clone_name},
            dry=True)
        with self.assertRaises(api.ServerArrayException):
            yield actor.execute()

    @attr('integration')
    @testing.gen_test(timeout=60)
    def integration_02a_clone(self):
        actor = server_array.Clone(
            'Clone %s' % self.template_array,
            {'source': self.template_array,
             'dest': self.clone_name})
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=30)
    def integration_02b_clone_with_duplicate_array(self):
        actor = server_array.Clone(
            'Clone %s' % self.template_array,
            {'source': self.template_array,
             'dest': self.clone_name})
        with self.assertRaises(api.ServerArrayException):
            yield actor.execute()

    @attr('integration')
    @testing.gen_test(timeout=30)
    def integration_02c_clone_with_missing_template(self):
        actor = server_array.Clone(
            'Clone missing array',
            {'source': 'unit-test-fake-array',
             'dest': self.clone_name})
        with self.assertRaises(api.ServerArrayException):
            yield actor.execute()

    @attr('integration')
    @testing.gen_test(timeout=60)
    def integration_03a_update_dry(self):
        actor = server_array.Update(
            'Update %s' % self.clone_name,
            {'array': self.clone_name}, dry=True)
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=60)
    def integration_03b_update_dry_missing_array(self):
        actor = server_array.Update(
            'Update missing array',
            {'array': 'unit-test-fake-array',
             'params': {}, 'inputs': {}}, dry=True)
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=60)
    def integration_04a_update_params(self):
        # Patch the array with some new min_instance settings, then launch it
        actor = server_array.Update(
            'Update %s' % self.clone_name,
            {'array': self.clone_name,
             'params': {'elasticity_params': {'bounds': {
                        'min_count': '1', 'max_count': '2'}},
                        'status': 'enabled',
                        'description': 'Unit Tests: %s' % UUID}})
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=60)
    def integration_04b_update_inputs(self):
        # There is no way to validate that the actual inputs were set right,
        # nor can we expect the end user to have the exact same server template
        # inputs that we want here. We can still execute the code though and
        # make sure it doesnt error out.
        actor = server_array.Update(
            'Update %s' % self.clone_name,
            {'array': self.clone_name,
             'inputs': {'TEST_INPUT': 'text:TEST_VALUE'}})
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=10)
    def integration_04c_update_with_invalid_params(self):
        actor = server_array.Update(
            'Update %s' % self.template_array,
            {'array': self.template_array,
             'params': {
                 'elasticity_params': {
                     'bounds': {'min_count': '5', 'max_count': '1'}}}})
        with self.assertRaises(exceptions.UnrecoverableActionFailure):
            yield actor.execute()

    @attr('integration')
    @testing.gen_test(timeout=60)
    def integration_04d_update_missing_array(self):
        # Patch the array with some new min_instance settings, then launch it
        actor = server_array.Update(
            'Update %s' % self.clone_name,
            {'array': self.clone_name,
             'params': {'elasticity_params': {'bounds': {
                        'min_count': '1', 'max_count': '2'}},
                        'status': 'enabled',
                        'description': 'Unit Tests: %s' % UUID}})
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=30)
    def integration_05a_launch_dry(self):
        # Launch the machines and wait until they boot
        actor = server_array.Launch(
            'Launch %s' % self.clone_name,
            {'array': self.clone_name}, dry=True)
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    # Note: These tests can run super slow -- the server boot time
    # itself may take 5-10 minutes, and sometimes Amazon and RightScale
    # slowdown. Give this test up to 30m to execute before we bail out.
    @attr('integration')
    @testing.gen_test(timeout=1800)
    def integration_05b_launch(self):
        # Launch the machines and wait until they boot
        actor = server_array.Launch(
            'Launch %s' % self.clone_name,
            {'array': self.clone_name})
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=120)
    def integration_06a_execute_dry(self):
        actor = server_array.Execute(
            'Execute %s' % self.clone_name,
            {'array': self.clone_name,
             'script': self.template_script,
             'inputs': {'SLEEP': 'text:15'}},
            dry=True)
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=120)
    def integration_06b_execute(self):
        actor = server_array.Execute(
            'Execute %s' % self.clone_name,
            {'array': self.clone_name,
             'script': self.template_script,
             'inputs': {'SLEEP': 'text:15'}})
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=300)
    def integration_07a_destroy_dry(self):
        actor = server_array.Destroy(
            'Destroy %s' % self.template_array,
            {'array': self.clone_name, 'terminate': True},
            dry=True)
        ret = yield actor.execute()
        self.assertEquals(True, ret)

    @attr('integration')
    @testing.gen_test(timeout=300)
    def integration_07b_destroy(self):
        actor = server_array.Destroy(
            'Destroy %s' % self.template_array,
            {'array': self.clone_name, 'terminate': True})
        ret = yield actor.execute()
        self.assertEquals(True, ret)
