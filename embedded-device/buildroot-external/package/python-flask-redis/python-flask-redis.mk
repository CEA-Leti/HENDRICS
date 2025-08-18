################################################################################
#
# python-flask-redis
#
################################################################################


PYTHON_FLASK_REDIS_VERSION = 0.4.0
PYTHON_FLASK_REDIS_SOURCE = flask-redis-$(PYTHON_FLASK_REDIS_VERSION).tar.gz
PYTHON_FLASK_REDIS_SITE = $(TOPDIR)/../embedded-device-app/redis
PYTHON_FLASK_REDIS_SITE_METHOD = local
PYTHON_FLASK_REDIS_SETUP_TYPE = setuptools
PYTHON_FLASK_REDIS_LICENSE = 
PYTHON_FLASK_REDIS_LICENSE_FILES = LICENSE.md

$(eval $(python-package))
