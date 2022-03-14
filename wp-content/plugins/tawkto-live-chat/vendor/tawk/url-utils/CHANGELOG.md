# 2.0.1

Fixed compatibility issue for PHP version >= 5.6.

# 2.0.0

## General changes

- [Breaking] Removed old matching modules.
	- `Tawk\Match\Path`
	- `Tawk\Match\Url`
- Added new modules for pattern matching.
	- `Tawk\Modules\PathPatternMatcher`
	- `Tawk\Modules\UrlPatternMatcher`
- Added new helpers for parsing URLs and paths.
	- `Tawk\Helpers\PathHelper`
	- `Tawk\Helpers\UrlHelper`
- Added new enum `Tawk\Enums\WildcardLocation`.

# 1.0.0

Initial Release
