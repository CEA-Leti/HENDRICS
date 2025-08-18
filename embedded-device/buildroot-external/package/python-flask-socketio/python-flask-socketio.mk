################################################################################
#
# python-flask-socketio
#
################################################################################


PYTHON_FLASK_SOCKETIO_VERSION =  5.3.6
PYTHON_FLASK_SOCKETIO_SOURCE = Flask-socketIO-$(PYTHON_FLASK_SOCKETIO_VERSION).tar.gz
PYTHON_FLASK_SOCKETIO_SITE = $(TOPDIR)/../embedded-device-app/socketio
PYTHON_FLASK_SOCKETIO_SITE_METHOD = local
PYTHON_FLASK_SOCKETIO_SETUP_TYPE = setuptools
PYTHON_FLASK_SOCKETIO_LICENSE = 
PYTHON_FLASK_SOCKETIO_LICENSE_FILES = LICENSE.md

$(eval $(python-package))
