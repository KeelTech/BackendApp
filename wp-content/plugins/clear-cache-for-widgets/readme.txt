=== Clear Cache for Me ===
Contributors: webheadllc
Donate link: https://webheadcoder.com/donate-clear-cache-for-me
Tags: wpengine, cache, clear, purge, js, css, widget
Requires at least: 3.8
Tested up to: 5.8
Stable tag: 1.7
License: GPLv2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html

Purges all cache on WPEngine, W3 Total Cache, WP Super Cache, WP Fastest Cache when updating widgets, menus, settings.  Forces a browser to reload CSS and JS files.

== Description ==

W3 Total Cache and WP Super Cache are great caching plugins, but they do not know when a widget is updated.  WPEngine is the best place to host your WordPress installation, but their caching system is no smarter when it comes to updating widgets and menus.  I created this plugin because my website did not see any changes when saving widgets or menus using these caching systems.  Clear Cache For Me will purge ALL your cache each time you do a save without having to press an additional button.  It may be overkill, which may be why it's not built in, but some people need simplicity.

In addition to clearing those pesky caching engines, Clear Cache for Me can force your browser to reload your current theme's CSS and JS files.  I modify my theme's CSS and JS files every so often and always have trouble with the browser not getting the latest version.  So now after clicking on the "Clear Cache Now!" button on the dashboard the browser will be forced to reload the current theme's CSS and JS files.  If you do not click the "Clear Cache Now!" button, the browser will cache the CSS and JS files like it normally does.

The popular Qode themes has a options to set your own custom CSS and JS.  Sometimes you may not see your changes for a long while because your browser is trying to get the cached file.  Whenever you save your Qode's options, the CSS and JS files will be forced to reload in the browser on the public side.

Works with the following caching systems:

* Autoptimize
* Breeze Cache
* Cache Enabler
* GoDaddy Cache
* Kinsta Cache
* LiteSpeed Cache
* SiteGround SuperCacher
* WP Fastest Cache
* WP Super Cache
* WP Optimize Cache
* W3 Total Cache
* WPEngine Cache


Clears all cache for following actions (requires a caching system above to be active):

* When Widgets are saved.
* When Customizer is saved.
* When Menus are saved.
* When a fields in Advanced Custom Fields are saved.
* When a Contact Form 7 form is saved.
* When a Formidable Form form is saved.
* When WooThemes settings are saved.
* When NextGen Gallery albums and galleries are updated (beta - may not clear cache on all actions).
* When Qode options are saved this plugin forces browsers to reload the custom css and custom js.
* When a WP Forms forms or settings are saved.
* When WooCommerce settings are saved. (Cache should already be clearing when products are saved.)
* When settings from the Insert Headers and Footers plugin by WPBeginner are saved.  
* When Settings from a settings page is saved.  This includes settings from WordPress core, Yoast SEO, and most other plugins using the Settings API.
* When WordPress is updated.
* When plugins are updated, activated, and deactivated.

[See the plugin's homepage for more details](https://webheadcoder.com/clear-cache-for-me/).

== Screenshots ==

1. The button on the dashboard.  

== Changelog ==

= 1.7 =
Added cache clearing when fields in Advanced Custom Fields are updated.  

= 1.6 =
Added cache clearing when WordPress core is updated.
Added cache clearing when plugins are activated, deactivated, and updated.  
Added cache clearing support for Insert Headers and Footers plugin.  
Fixed admin-bar loading when admin bar is not present.    

= 1.5.1 =
Remove ajax from admin bar when jQuery is not available.  

= 1.5 =
Updated admin bar link to clear cache in place.  
Added cache clearing support for Cache Enabler.  
Fixed cache clearing for Breeze.  

= 1.4.1 =
Updated Clear Cache For Me button in admin bar.  
Updated clearing WP Fastest Cache to include clearing minified cache.  
(thanks to Ov3rfly)  

= 1.4 =
Added cache clearing for LiteSpeed Cache.  
Added cache clearing for SiteGround SuperCacher.  
Added cache clearing for Autoptimize.  
Added Clear Cache For Me button in admin bar.  
Added Development Mode to always load a fresh copy of javascript and stylesheet files.  

= 1.3 =
Added cache clearing for Breeze cache.
Added cache clearing when WP Forms is saved
Added cache clearing when WooCommerce settings are saved.
Moved the settings to its own page under Settings.  
Fixed cache clearing for GoDaddy so all pages are cleared.

= 1.2 =
Added cache clearing for WP Optimize cache.

= 1.1.1 =
removed hosting notice, fixed js error.  

= 1.1 =
Added cache clearing for Kinsta hosting.  
Added cache clearing for GoDaddy manged hosting.  
Added cache clearing for Formidable Forms.  

= 1.0 =
Added clearing cache for all JS and CSS theme files.  
Added clearing cache when Qode theme options are saved.  

= 0.93 =
Fixed button not showing up when admin doesn't have permissions.  Button will now always show for the admin user with manage_options capability.  

= 0.92 =
Fixed clearing cache on widgets when widgets are saved or reordered.  

= 0.91 =
Minor fix checking if certain WPEngine functions exist.  Thanks to @tharmann!  

= 0.9 =
Added clear cache for NextGen Gallery saving, but not sure if all actions are accounted for.

= 0.8 =
Added clear cache for WooThemes options.  
Fixed cache not clearing on some WP Super Cache installations.

= 0.7.1 =
Added clear cache for settings pages.  
Added clear cache for Contact Form 7 form saving.  
Updated description and added donation link on plugin page only.

= 0.6.2 =
minor updates to css class names

= 0.6.1 =
Updated German translation (thanks to Ov3rfly!).  
Updated admin HTML and styles (thanks to Ov3rfly!).

= 0.6 =
Fixed cache not clearing when widgets are re-ordered or deleted (thanks to Ov3rfly!).  
Added optional instructions to be shown above the button (thanks to Ov3rfly!).  
Added to and updated German translations (thanks to Ov3rfly!).  
Added more security checks. (thanks to Ov3rfly!).  
Added customize theme detection.  Clears cache when customizing theme.  
Reorganized code a bit.

= 0.5 =
Added German language translation (thanks to Ov3rfly)  
Added hooks for 3rd party code.

= 0.4 =
Bug fixed: Fixed cache not clearing when updating nav menu. (thanks to Ov3rfly for catching this and supplying the fix)

= 0.3 =
Added clear caching for menus  
Added clear cache button to dashboard  
Added option to set what capability is needed to view the clear cache button for admins.  

= 0.2 =
Removed garbage at the end of the plugin url.

= 0.1 =
Initial release.


== Developer Options ==

= ccfm_supported_caching_exists =  
Use this filter to determine if this plugin should do anything including showing the button on the dashboard.  Return true if a caching system is supported.  
Default: True if any of the supported caching systems is active.  
See Example 1 below.

= ccfm_admin_init or ccfm_init_actions =  
Use this action to add hooks when cache is to be cleared.  Or do any other setup activity.  

= ccfm_clear_cache_for_me_before = 
Use this action to clear cache from an unsupported caching system before the default caching systems clear their cache.

= ccfm_clear_cache_for_me = 
Use this action to clear cache from an unsupported caching system after the default caching systems clear their cache.


= Example = 
If you were using an unsupported caching system you'll need to identify the caching plugin's class or function which clears the cache.  As an example, if the unsupported caching system called the `MyOtherCache::clear_all()` function, you would use the following code to get this plugin to clear the cache.

`<?php
function my_other_cache_enable( $return = false ) {
    if ( class_exists( 'MyOtherCache' ) )
        return true;
    return $return;
}
add_filter('ccfm_supported_caching_exists', 'my_other_cache_enable');

function my_other_cache_clear() {
    if ( my_other_cache_enable() )
        MyOtherCache::clear_all();
}
add_action('ccfm_clear_cache_for_me', 'my_other_cache_clear');`

