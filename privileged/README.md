# Privileged broker design placeholder

The alpha repository intentionally does not install a root action helper.
The default configuration therefore enables no actions. The enumerated catalog
and unprivileged client are API scaffolding, not an authorization boundary.

The future broker must:

- run independently of the interactive SSH identity;
- accept only identifiers from `pitft_oob.actions.catalog`;
- reject additional arguments, environment overrides, and executable paths;
- enforce per-action capability policy and rate limits;
- log request identity and outcome without logging credentials;
- require release-before-confirm and a completed UI hold for destructive actions,
  while independently retaining the right to reject any request;
- have parser, authorization, symlink/path, race, and failure-injection tests.

Do not replace this with a generic passwordless sudo rule.
