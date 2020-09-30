# SETUP (INSTALL)
install-all: \
 install-sdk \
 install-schema-validator \
 install-iteratively \
 install-amplitude \
 install-mixpanel \
 install-segment \
 install-snowplow

install-sdk:
	cd ./packages/sdk/; poetry install

install-amplitude:
	cd ./packages/plugin-amplitude/; poetry install

install-iteratively:
	cd ./packages/plugin-iteratively/; poetry install

install-mixpanel:
	cd ./packages/plugin-mixpanel/; poetry install

install-schema-validator:
	cd ./packages/plugin-schema-validator/; poetry install

install-segment:
	cd ./packages/plugin-segment/; poetry install

install-snowplow:
	cd ./packages/plugin-snowplow/; poetry install

# BUILD
build-all: \
 build-sdk \
 build-schema-validator \
 build-iteratively \
 build-amplitude \
 build-mixpanel \
 build-segment \
 build-snowplow

build-sdk:
	cd ./packages/sdk/; poetry build

build-amplitude:
	cd ./packages/plugin-amplitude/; poetry build

build-iteratively:
	cd ./packages/plugin-iteratively/; poetry build

build-mixpanel:
	cd ./packages/plugin-mixpanel/; poetry build

build-schema-validator:
	cd ./packages/plugin-schema-validator/; poetry build

build-segment:
	cd ./packages/plugin-segment/; poetry build

build-snowplow:
	cd ./packages/plugin-snowplow/; poetry build

# PUBLISH (Test PyPi)
publish-test-all: \
 publish-test-sdk \
 publish-test-schema-validator \
 publish-test-iteratively \
 publish-test-amplitude \
 publish-test-mixpanel \
 publish-test-segment \
 publish-test-snowplow

publish-test-sdk:
	cd ./packages/sdk/; poetry publish -r testpypi

publish-test-amplitude:
	cd ./packages/plugin-amplitude/; poetry publish -r testpypi

publish-test-iteratively:
	cd ./packages/plugin-iteratively/; poetry publish -r testpypi

publish-test-mixpanel:
	cd ./packages/plugin-mixpanel/; poetry publish -r testpypi

publish-test-schema-validator:
	cd ./packages/plugin-schema-validator/; poetry publish -r testpypi

publish-test-segment:
	cd ./packages/plugin-segment/; poetry publish -r testpypi

publish-test-snowplow:
	cd ./packages/plugin-snowplow/; poetry publish -r testpypi

# PUBLISH (PyPi)
publish-all: \
 publish-sdk \
 publish-schema-validator \
 publish-iteratively \
 publish-amplitude \
 publish-mixpanel \
 publish-segment \
 publish-snowplow

publish-sdk:
	cd ./packages/sdk/; poetry publish

publish-amplitude:
	cd ./packages/plugin-amplitude/; poetry publish

publish-iteratively:
	cd ./packages/plugin-iteratively/; poetry publish

publish-mixpanel:
	cd ./packages/plugin-mixpanel/; poetry publish

publish-schema-validator:
	cd ./packages/plugin-schema-validator/; poetry publish

publish-segment:
	cd ./packages/plugin-segment/; poetry publish

publish-snowplow:
	cd ./packages/plugin-snowplow/; poetry publish
