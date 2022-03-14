<?php

namespace Tawk\Helpers;

class Common {
	/**
	 * Checks the provided text starts with.
	 *
	 * @param  string $text The text to be checked
	 * @param  string $start_with The text to match from the provided text to start with.
	 * @return void
	 */
	public static function text_starts_with($text, $start_with) {
		$length = strlen($start_with);
		return substr($text, 0, $length) === $start_with;
	}

	/**
	 * Checks the provided text ends with.
	 *
	 * @param  string $text      The text to be checked
	 * @param  string $ends_with The text to match from the provided text to start with.
	 * @return void
	 */
	public static function text_ends_with($text, $ends_with) {
		$length = strlen($ends_with);
		return substr($text, -$length) === $ends_with;
	}
}
