<?php

namespace Tawk\Models;

use Tawk\Enums\WildcardLocation;
use Tawk\Helpers\PathHelper;

class PathPattern {
	protected $path_chunks;
	protected $wildcard_location;
	protected $strict_length_flag;

	/**
	 * Constructor
	 *
	 * @param  string $path URL Path
	 */
	protected function __construct($path) {
		$this->path_chunks = PathHelper::get_chunks($path);
		$this->wildcard_location = PathHelper::get_wildcard_location_by_chunks($this->path_chunks);
		$this->strict_length_flag = PathHelper::path_has_strict_length($path, $this->wildcard_location);
	}

	/**
	 * Creates an instance of PathPattern class from the provided path.
	 *
	 * @param  string $path URL Path.
	 * @return PathPattern instance of PathPattern Model.
	 */
	public static function create_instance_from_path($path) {
		return new PathPattern($path);
	}

	/**
	 * Checks if path has wildcard.
	 *
	 * @return bool Returns `true` if path has wildcard. Otherwise, `false`.
	 */
	public function has_wildcard() {
		return $this->wildcard_location !== WildcardLocation::NONE;
	}

	/**
	 * Checks if path should have strict length.
	 *
	 * @return bool Returns `true` if path should have strict length. Otherwise, `false`.
	 */
	public function has_strict_length() {
		return $this->strict_length_flag;
	}

	/**
	 * Provides the path in chunks.
	 *
	 * @return string[] Path chunks.
	 */
	public function get_chunks() {
		return $this->path_chunks;
	}

	/**
	 * Provides the wildcard location.
	 *
	 * @return string Wildcard location.
	 */
	public function get_wildcard_location() {
		return $this->wildcard_location;
	}
}
