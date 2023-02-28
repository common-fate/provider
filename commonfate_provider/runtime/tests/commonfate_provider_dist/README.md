This package is used to simulate a packaged provider for unit tests.

The PDK packages the provider as `commonfate_provider_dist`.

In our tests, we manually append this to the Python path and then import the runtime to verify it works properly.
