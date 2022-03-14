<?php

namespace Tawk\Helpers;

use Tawk\Helpers\PathHelper;

define('PROTOCOL_REGEX', '/^(http|https):\/\//');

class UrlHelper {
	/**
	 * Parses url
	 *
	 * @param  string $url
	 *
	 * @return array {
	 *  path: string,
	 *  host: string?,
	 *  port: string?,
	 *  scheme: string?
	 * }
	 */
	public static function parse_url($url) {
		$is_path = PathHelper::is_path($url);
		$has_protocol = preg_match(PROTOCOL_REGEX, $url) === 1;

		if ($is_path === false && $has_protocol === false) {
			// Add http:// in front of the string to properly parse the provided url.
			// The reason is if the url provided only consists of the following example:
			//
			// www.example.com/path/to/somewhere
			//
			// parse_url function will treat the whole url as a path.
			$url = 'http://'.$url;
		}

		$parsed_url = parse_url($url);

		$url_data = array(
			'path' => '/'
		);

		if (isset($parsed_url['path'])) {
			$url_data['path'] = $parsed_url['path'];
		}

		if (isset($parsed_url['host'])) {
			$url_data['host'] = $parsed_url['host'];
		}

		if (isset($parsed_url['port'])) {
			$url_data['port'] = $parsed_url['port'];
		}

		if ($is_path === false && $has_protocol === true) {
			$url_data['scheme'] = $parsed_url['scheme'];
		}

		return $url_data;
	}
}
