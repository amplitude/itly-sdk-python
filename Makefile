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

publish-test-all: publish-test-sdk publish-test-amplitude publish-test-iteratively publish-test-mixpanel publish-test-schema-validator publish-test-segment

publish-all: publish-sdk publish-amplitude publish-iteratively publish-mixpanel publish-schema-validator publish-segment

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
