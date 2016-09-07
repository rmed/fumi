# Changelog

## 0.4.0 - unreleased

### Added
- Optional configuration fields: `buffer-size` and `shared-paths`
- `prepare` command to test connection and create remote directory tree
- Localization of application

### Changed
- Documentation was rewritten using Sphinx
- Major code refactoring


## 0.3.0 - Sep 22nd, 2015

### Added
- Allow connecting with password instead of public key
- Added `use-password` and `password` fields to deployment file

### Changed
- Improved output format
- Changed how remote command output is displayed


## 0.2.0 - May 9th, 2015

### Added
- Allow ignoring specific files and directories for `local` deployment type
- Try to create remote directory trees if they do not exist already
- Added basic rollback

### Changed
- Improved output structure and formatting
- Minor update to documentation
- Changed the way pre and post-deployment commands are written and executed


## 0.1.1 - March 23rd, 2015

### Changed
- Initial release
