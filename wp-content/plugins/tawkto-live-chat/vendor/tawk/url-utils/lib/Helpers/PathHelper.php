<?php

namespace Tawk\Helpers;

use Tawk\Enums\WildcardLocation;

define('WILDCARD', '*');

class PathHelper {
	/**
	 * Gets the WILDCARD constant.
	 *
	 * @return string Wildcard
	 */
	public static function get_wildcard() {
		return WILDCARD;
	}

	/**
	 * Checks if provided path starts with the WILDCARD or /.
	 * If it is, it is considered as a path.
	 *
	 * @param  string $path URL Path.
	 * @return bool Returns `true` if the provided path either has a leading `/` or WILDCARD. Otherwise, returns `false`.
	 */
	public static function is_path($path) {
		return strpos($path, WILDCARD) === 0 || strpos($path, '/') === 0;
	}

	/**
	 * Checks if the pattern chunks provided has a wildcard
	 *
	 * @param  string[] $path_chunks URL Path in chunks.
	 * @return bool Returns `true` if there's a WILDCARD in the provided path chunks. Otherwise, returns `false`.
	 */
	public static function path_chunks_has_wildcard($path_chunks) {
		return in_array(WILDCARD, $path_chunks, true);
	}

	/**
	 * Checks if the pattern chunk provided is a wildcard.
	 *
	 * @param  string $path_chunk URL Path chunk.
	 * @return bool Returns `true` if the chunk is a WILDCARD. Otherwise, returns `false`.
	 */
	public static function is_wildcard($path_chunk) {
		return $path_chunk === WILDCARD;
	}

	/**
	 * Gets the path chunks from the provided path.
	 *
	 * @param  string $path URL Path.
	 * @return string[] URL Path in chunks.
	 */
	public static function get_chunks($path) {
		$chunks = explode('/', $path);
		$filtered_chunks = array_filter($chunks, function ($item) {
			return empty($item) !== true;
		});
		return array_values($filtered_chunks);
	}

	/**
	 * Identifies where the wildcard is located in the provided chunks.
	 *
	 * @param  string[] $path_chunks URL Path in chunks.
	 * @return string Wildcard Location.
	 */
	public static function get_wildcard_location_by_chunks($path_chunks) {
		if (is_array($path_chunks) === false) {
			return WildcardLocation::NONE;
		}

		if (self::path_chunks_has_wildcard($path_chunks) === false) {
			return WildcardLocation::NONE;
		}

		if (self::is_wildcard(end($path_chunks))) {
			return WildcardLocation::END;
		}

		if (self::is_wildcard($path_chunks[0])) {
			return WildcardLocation::START;
		}

		return WildcardLocation::MIDDLE;
	}

	/**
	 * Check if path has strict length.
	 *
	 * @param  string $path              URL Path.
	 * @param  string $wildcard_location Wildcard Location.
	 * @return bool Returns `true` if path has strict length. Otherwise, returns `false`.
	 */
	public static function path_has_strict_length($path, $wildcard_location) {
		if ($wildcard_location === WildcardLocation::START && Common::text_starts_with($path, '/' . WILDCARD) === true) {
			return true;
		}

		if ($wildcard_location === WildcardLocation::END && Common::text_ends_with($path, WILDCARD . '/') === true) {
			return true;
		}

		return false;
	}
}
