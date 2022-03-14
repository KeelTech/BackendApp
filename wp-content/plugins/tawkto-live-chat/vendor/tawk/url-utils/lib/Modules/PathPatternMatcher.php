<?php

namespace Tawk\Modules;

use Tawk\Enums\WildcardLocation;
use Tawk\Helpers\PathHelper;
use Tawk\Models\PathPattern;

class PathPatternMatcher {
	/**
	 * Matches current path to multiple patterns
	 *
	 * @param  string[] $current_path_chunks Current path in chunks
	 * @param  PathPattern[] $path_patterns  List of path pattern instances
	 * @return bool Returns `true` if current path chunks matches with one of the provided patterns. Otherwise, returns `false`.
	 */
	public static function match($current_path_chunks, $path_patterns) {
		foreach($path_patterns as $path_pattern) {
			$path_pattern_chunks = $path_pattern->get_chunks();
			$has_strict_length = $path_pattern->has_strict_length();

			if ($path_pattern->has_wildcard() === false) {
				if (join('/', $current_path_chunks) === join('/', $path_pattern_chunks)) {
					return true;
				};
			} else if ($path_pattern->get_wildcard_location() === WildcardLocation::START) {
				// if wildcard is at the start, match in reverse order so that the wildcard is at the end
				if (self::match_chunks_reverse($current_path_chunks, $path_pattern_chunks, $has_strict_length) === true) {
					return true;
				}
			} else {
				if (self::match_chunks($current_path_chunks, $path_pattern_chunks, $has_strict_length) === true) {
					return true;
				}
			}
		}

		return false;
	}

	/**
	 * Iterates over the current and pattern path chunks and matches them
	 *
	 * @param  string[] $current_path_chunks Current path in chunks
	 * @param  string[] $pattern_path_chunks Pattern path in chunks
	 * @return boolean Returns `true` if current path matches with the pattern. Otherwise, `false`.
	 */
	private static function match_chunks($current_path_chunks, $pattern_path_chunks, $has_strict_length) {
		$current_path_len = count($current_path_chunks);
		$pattern_path_len = count($pattern_path_chunks);

		// do not proceed on matching if pattern path has strict length
		// and if it differs to the current path length.
		if ($has_strict_length === true && $current_path_len !== $pattern_path_len) {
			return false;
		}

		// handles empty current path
		if ($current_path_len === 0) {
			// match if pattern path is also empty
			if ($pattern_path_len === 0) {
				return true;
			}

			// match if pattern path is only a wildcard
			if ($pattern_path_len === 1 && PathHelper::is_wildcard($pattern_path_chunks[0])) {
				return true;
			}

			// else, do not match since there's nothing to match with
			return false;
		}

		// do not proceed on matching if pattern path is longer than the current path.
		if ($pattern_path_len > $current_path_len) {
			return false;
		}

		for ($i = 0; $i < $current_path_len; $i++) {
			$current_path_chunk = $current_path_chunks[$i];

			// handles current paths that are longer than the pattern
			// ex.
			//   path - /path/to/somewhere/longer
			//   pattern - /path/*/somewhere
			if (isset($pattern_path_chunks[$i]) === false) {
				return false;
			}

			$pattern_path_chunk = $pattern_path_chunks[$i];

			if (PathHelper::is_wildcard($pattern_path_chunk)) {
				// if current pattern chunk is the last chunk
				if ($i === $pattern_path_len - 1) {
					// if pattern does not have strict length
					// stop matching and true
					if ($has_strict_length === false) {
						return true;
					}
				}

				// otherwise, continue on matching
				continue;
			}

			// stop matching if one of the chunks doesn't match.
			if ($pattern_path_chunk !== $current_path_chunk) {
				return false;
			}
		}

		return true;
	}

	/**
	 * Iterates over the current and pattern path chunks and matches them in reverse
	 *
	 * @param  string[] $current_path_chunks Current path in chunks
	 * @param  string[] $pattern_path_chunks Pattern path in chunks
	 * @return boolean Returns `true` if current path matches with the pattern. Otherwise, `false`.
	 */
	private static function match_chunks_reverse($current_path_chunks, $pattern_path_chunks, $has_strict_length) {
		$current_path_len = count($current_path_chunks);
		$pattern_path_len = count($pattern_path_chunks);

		// do not proceed on matching if pattern path has strict length
		// and if it differs to the current path length.
		if ($has_strict_length === true && $current_path_len !== $pattern_path_len) {
			return false;
		}

		// handles empty current path
		if ($current_path_len === 0) {
			// match if pattern path is also empty
			if ($pattern_path_len === 0) {
				return true;
			}

			// match if pattern path is only a wildcard
			if ($pattern_path_len === 1 && PathHelper::is_wildcard($pattern_path_chunks[0])) {
				return true;
			}

			// else, do not match since there's nothing to match with
			return false;
		}

		// do not proceed on matching if pattern path is longer than the current path.
		if ($pattern_path_len > $current_path_len) {
			return false;
		}

		$offset = $current_path_len - $pattern_path_len;
		for ($i = $current_path_len - 1; $i >= 0; $i--) {
			$current_path_chunk = $current_path_chunks[$i];

			// handles current paths that are longer than the pattern
			// ex.
			//   path - /path/to/somewhere/longer
			//   pattern - */somewhere
			$pattern_index = $i - $offset;
			if (isset($pattern_path_chunks[$pattern_index]) === false) {
				return false;
			}

			$pattern_path_chunk = $pattern_path_chunks[$pattern_index];

			if (PathHelper::is_wildcard($pattern_path_chunk)) {
				// if current pattern chunk is the first chunk
				if ($pattern_index === 0) {
					// if pattern does not have strict length
					// stop matching and true
					if ($has_strict_length === false) {
						return true;
					}
				}

				// otherwise, continue on matching
				continue;
			}

			// stop matching if one of the chunks doesn't match.
			if ($pattern_path_chunk !== $current_path_chunk) {
				return false;
			}
		}

		return true;
	}
}
