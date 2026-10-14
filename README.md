# Cupergram APK updates

[Download Cupergram 71359](https://github.com/RastyDima/cupergram-updates/releases/download/cupergram-38536937180/Cupergram-12.10.6.apk) · [APK, SHA256 and corresponding sources](https://github.com/RastyDima/cupergram-updates/releases/tag/cupergram-38536937180).

Successful signed builds are published independently from Android emulator checks. The channel verifies the APK checksum, original signing certificate, package and version before updating the public feed. APK 71359 has not passed the full emulator suite; [Android check results](https://github.com/RastyDima/cupergram/actions/runs/38566291880) are shown separately. This is recorded as `androidVerified: false` in the feed.

The app reads [update.json](https://raw.githubusercontent.com/RastyDima/cupergram-updates/main/update.json) without a GitHub login, checks SHA256 and requires the package and signing certificate to match the installed app. Installation requires Android's confirmation.

Each release includes the APK, SHA256 and corresponding sources (GPL v2 or later). Telegram account credentials and signing private keys are not included. The source repository stays separate from this distribution channel.
