'use strict';

try {
	importScripts(
		'bg/background.js',
		'bg/storage_monitor.js'
	);
} catch (e) {
	console.error('bg: Error:', e);
}
