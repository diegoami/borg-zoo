# Recovered original configuration files (#113)

These gzip-compressed, content-addressed files are original `user/borg.txt` bytes from retained
workflow artifacts, not reconstructions from a source checkout or defaults.
`manifest.json` records the source artifact URL, ZIP/TGZ SHA-256 and member paths.
The recovery tool checks each TGZ against its artifact checksum receipt.

The report uses a file only if its SHA-256 matches that game's existing
`config_sha256`. Equal hashes permit deduplication across games. Historical
results on the results branch are unchanged. An absent file is explicitly
unavailable; requested overrides and native-reported settings remain separate.

Recovered evidence covers the 36-game town-class smoke and a completed PR85
shard. The original joint-confirmation workflow retained no raw configuration
artifact; its inspector therefore reports the historical file unavailable.

Reproduce recovery with `python3 tools/recover-configurations.py ARTIFACT.zip
SOURCE_ARTIFACT_URL`. Do not substitute the build's base borg.txt for a game's
written file.
