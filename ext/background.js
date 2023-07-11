'use strict';

try {
	importScripts(
		'bg/api_config.js',
		'bg/utils.js',
		'bg/background.js',
		'bg/storage_monitor.js',
		'bg/site_parser.js'
	);
} catch (e) {
	console.error('bg: Error:', e);
}
