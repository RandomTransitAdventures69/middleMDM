# Releases

Pushing a version tag matching `v*` runs the release workflow:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

The workflow runs the test suite on Linux and macOS, builds native client executables on Windows, Linux, and macOS, and publishes installable server source bundles for Linux and macOS plus a platform-neutral server source archive. macOS assets include the architecture reported by the GitHub runner. Client bundles include the setup guide; Windows bundles also include the service installer. Server bundles include an installer, launcher, and server setup documentation.

The client supports Python installations as well as standalone release binaries. Use the instructions in [Client Setup](client-setup.md) for configuration and service setup. See [Server Package](server-package.md) for the macOS and Linux server bundles.
