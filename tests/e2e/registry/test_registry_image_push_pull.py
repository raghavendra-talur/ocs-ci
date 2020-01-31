import logging
import pytest
from ocs_ci.framework.testlib import tier1, E2ETest
from ocs_ci.ocs import ocp, registry, constants
from ocs_ci.framework import config

logger = logging.getLogger(__name__)


class TestRegistryImagePullPush(E2ETest):
    """
    Test to check Image push and pull worked with registry backed by OCS
    """

    @tier1
    @pytest.mark.polarion_id("OCS-1080")
    def test_registry_image_pull_push(self):
        """
        Test case to validate registry image pull and push with OCS backend

        """
        image_url = 'docker.io/library/busybox'

        # Get openshift registry route and certificate access
        registry.enable_route_and_create_ca_for_registry_access()

        # Add roles to user so that user can perform image pull and push to registry
        registry.add_role_to_user(role_type='registry-viewer', user=config.RUN['username'])
        registry.add_role_to_user(role_type='registry-editor', user=config.RUN['username'])
        registry.add_role_to_user(role_type='system:registry', user=config.RUN['username'])
        registry.add_role_to_user(role_type='admin', user=config.RUN['username'])
        registry.add_role_to_user(role_type='system:image-builder', user=config.RUN['username'])

        # Provide write access to registry
        ocp_obj = ocp.OCP()
        read_only_cmd = f"set env deployment.apps/image-registry REGISTRY_STORAGE_MAINTENANCE_READONLY- " \
            f"-n {constants.OPENSHIFT_IMAGE_REGISTRY_NAMESPACE}"
        ocp_obj.exec_oc_cmd(read_only_cmd)

        # Pull image using podman
        registry.image_pull(image_url=image_url)

        # Push image to registry using podman
        registry.image_push(
            image_url=image_url, namespace=constants.OPENSHIFT_IMAGE_REGISTRY_NAMESPACE
        )

        # List the images in registry
        img_list = registry.image_list_all()
        logger.info(f"Image list {img_list}")

        # Check either image present in registry or not
        registry.check_image_in_registry(image_url=image_url)
