=== YITH WooCommerce Affiliates ===

Contributors: yithemes
Tags:  affiliate, affiliate marketing, affiliate plugin, affiliate tool, affiliates, woocommerce affiliates, woocommerce referral, lead, link, marketing, money, partner, referral, referral links, referrer, sales, woocommerce, wp e-commerce, affiliate campaign, affiliate marketing, affiliate plugin, affiliate program, affiliate software, affiliate tool, track affiliates, tracking, affiliates manager, yit, yith, yithemes, yit affiliates, yith affiliates, yithemes affiliates
Requires at least: 5.7
Tested up to: 5.9
Stable tag: 1.14.0
License: GPLv2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html

YITH WooCommerce Affiliates allows you to create affiliate profiles and grant your affiliates earnings each time someone purchases from their link.

== Description ==

Do you want to improve your sales by sharing advertising of your products and of your site on other blogs to get visibility? But, maybe, you have not the time and the patience to browse the web in search of the right ones? No problem, you can let your users share your products on their sites and blogs in exchange of a commission for each product sold. Don’t you know how to do? No problem, again: you are in the right place, because here you find YITH WooCommerce Affiliates that makes this for you in a few clicks. Try it and you'll see on your own how it works!

= Free Features =

* When a user visits the store with a refer ID in query string, the plugin saves the affiliate ID and credits commissions to him/her if this visit turns into purchase
* Refer ID will be stored in user's cookie for a time that can be set in admin panel; this way, even though visit and purchase do not happen during the same navigation session, commissions can be credited correctly
* You can credit commissions only to affiliates that have registered and have been enabled correctly
* You can create new affiliates directly from users registered to your site
* You can use a shortcode to allow affiliate registration
* You can set a general commission for affiliates for each order coming from their refer ID
* Commission status changes automatically each time order status changes
* The plugin manages automatically all totals concerning affiliates and updates them according to the status of commissions and orders
* The plugin calculates automatically refunds and decrements the total of affiliate commissions in case of refunds
* You can register payments that have to be made to affiliates
* You can handle basic reports that can be filtered by date
* You can customise parameters for the cookies managed by the plugin
* Affiliates can access their own dashboard, where they find all information about sales trend
* You can use the shortcode "Generate link" to generate links for taking users to your site with the correct refer ID

== Installation ==

1. Unzip the downloaded zip file.
2. Upload the plugin folder into the `wp-content/plugins/` directory of your WordPress site.
3. Activate `YITH WooCommerce Affiliates` from Plugins page

YITH WooCommerce Affiliates will add a new submenu called "Affiliates" under "YITH" menu. Here you are able to configure all the plugin settings.

== Screenshots ==

1. [Admin] List of commissions
2. [Admin] List of affiliates
3. [Admin] List of payments
4. [Admin] Marketplace stats
5. [Admin] Marketplace settings
6. [Users] Affiliate dashboard
7. [Users] List of commissions
8. [Users] Click lists
9. [Users] List of payments
10. [Users] Link generator
11. [Users] User settings
12. [Users] Affiliate settings

== Changelog ==

= 1.14.0 - Released on 27 January 2022 =

* New: support for WooCommerce 6.2
* Update: YITH Plugin Framework
* Fix: WooCommerce Version error on update

= 1.13.0 - Released on 11 January 2022 =

* New: support for WordPress 5.9
* New: support for WooCommerce 6.1
* Update: YITH Plugin Framework

= 1.12.0 - Released on 15 December 2021 =

* New: support for WooCommerce 6.0
* Update: YITH Plugin Framework

= 1.11.0 - Released on 08 November 2021 =

* New: support for WooCommerce 5.9
* Update: YITH Plugin Framework

= 1.10.0 - Released on 11 October 2021 =

* New: support for WooCommerce 5.8
* Update: YITH Plugin Framework

= 1.9.1 - Released on 27 September 2021 =

* Update: YITH Plugin Framework
* Fix: debug info feature removed for all logged in users

= 1.9.0 - Released on 23 September 2021 =

* New: support for WooCommerce 5.7
* Update: YITH Plugin Framework
* Fix: product search box in Affiliate Dashboard page

= 1.8.7 - Released on 05 August 2021 =

* New: support for WooCommerce 5.6
* New: support for WordPress 5.8
* Update: YITH Plugin Framework
* Dev: new params on filter 'yith_wcaf_use_percentage_rates'
* Dev: added yith_wcaf_show_if_affiliate_result filter, to allow custom rules for yith_wcan_show_if_affiliate shortcode

= 1.8.5 - Released on 16 June 2021 =

* New: support for WooCommerce 5.4
* Update: YITH Plugin Framework
* Tweak: minor style improvements for admin panel

= 1.8.4 - Released on 13 May 2021 =

* New: support for WooCommerce 5.3
* Update: YITH Plugin Framework
* Tweak: minor style improvements for admin view
* Dev: added new yith_wcaf_payments_table_column_amount filter

= 1.8.3 - Released on 20 April 2021 =

* New: support for WooCommerce 5.2
* Update: YITH Plugin Framework
* Update: new panel style
* Dev: added new yith_wcaf_requester_origin filter

= 1.8.2 - Released on 12 March 2021 =

* New: support for WordPress 5.7
* New: support for WooCommerce 5.1
* Update YITH Plugin Framework
* Update: Italian language
* Dev: added new yith_wcaf_set_ref_cookie filter

= 1.8.1 - Released on 18 January 2021 =

* New: support for WooCommerce 5.0
* New: German language
* Update: YITH Plugin Framework
* Update: Dutch language

= 1.8.0 - Released on 12 January 2021 =

* New: support for WooCommerce 4.9
* Update: plugin framework
* Dev: added function yith_wcaf_number_format to format the rates

= 1.7.9 - Released on 09 December 2020 =

* New: support for WooCommerce 4.8
* Update: plugin framework
* Dev: added filter yith_wcaf_display_format in order to allow to change the format on conversion rate and rate section

= 1.7.7 - Released on 10 November 2020 =

* New: support for WordPress 5.6
* New: support for WooCommerce 4.7
* New: possibility to update plugin via WP-CLI
* Update: plugin framework
* Dev: removed deprecated method .ready from scripts

= 1.7.6 - Released on 15 October 2020 =

* New: support for WooCommerce 4.6
* Update: plugin framework
* Tweak: show correct currency for commissions on admin table
* Tweak: removed usage of deprecated jQuery method $.fn.toggle from admin assets
* Dev: added new filter yith_wcaf_commissions_dashboard_commissions

= 1.7.5 - Released on 17 August 2020 =

* New: support for WooCommerce 4.5
* Update: plugin framework
* Tweak: improved show_if_affiliates shortcode, to accept more than one rule, and to accept negated rules too
* Fix: plugin not consider bottom select for bulk actions on Commissions, Payments and Affiliates views

= 1.7.4 - Released on 13 August 2020 =

* New: support for WordPress 5.5
* New: support for WooCommerce 4.4
* New: breadcrumb for Affiliate Dashboard now contains link to get back to Dashboard home
* Update: plugin framework
* Tweak: added affiliate handling to REST api that creates order
* Tweak: affiliate now logs out directly from affiliate dashboard
* Fix: improved affiliate profile update, to avoid affiliate not having correct role
* Dev: added yith_wcaf_max_rate_value filter
* Dev: added yith_wcaf_line_item_commission_total filter
* Dev: added yith_wcaf_line_total_check_amount_total filter

= 1.7.3 - Released on 09 June 2020 =

* New: support for WooCommerce 4.2
* Tweak: fixed wrong text domain for some strings
* Fix: losing status selection after filtering on admin views
* Dev: added yith_wcaf_create_item_commission filter
* Dev: added yith_wcaf_enqueue_fontello_stylesheet filter
* Dev: add second parameter on yith_wcaf_use_percentage_rates hook

= 1.7.2 - Released on 08 May 2020 =

* New: support for WooCommerce 4.1
* Update: plugin framework
* Tweak: hotfix paypal return url, to set back affiliate cookie when getting back to site after cancelling order
* Fix: removed translation on screen id, that was causing missing assets on admin on non-english sites

= 1.7.1 - Released on 20 April 2020 =

* Update: plugin framework
* Update: Italian language
* Tweak: moved script localization just after script registration
* Tweak: minor improvements to frontend layouts, for better theme integration
* Tweak: removed not-pertinent CSS rules (this styling should be demanded by theme)
* Tweak: added affiliate dashboard shortcode as gutenberg block on brand new Dashboard page

= 1.7.0 - Released on 09 March 2020 =

* New: support for WordPress 5.4
* New: support for WooCommerce 4.0
* New: Greek translation
* New: added option to set up affiliates cookie via AJAX call (to better work with cache systems)
* New: added Elementor widgets
* Tweak: include commissions metabox into WC Subscription edit page
* Tweak: code reformat and improvements for PHPCS
* Update: plugin framework

= 1.6.9 – Released on 23 December 2019 =

* New: support for WooCommerce 3.9
* Update: plugin framework

= 1.6.8 - Released on 12 December 2019 =

* Update: plugin framework

= 1.6.7 - Released on 29 November 2019 =

* New: added category column to commissions table
* Tweak: check if dependencies are registered in order to prevent error in gutenberg pages
* Update: notice handler
* Update: plugin framework
* Fix: prevent warning when global $post do not contain WP_Post object

= 1.6.6 - Released on 06 November 2019 =

* Tweak: changed Fontello class names to avoid conflicts with themes
* Tweak: added checks before Fontello style inclusion, to load it just when needed

= 1.6.5 – Released on 05 November 2019 =

* New: support for WordPress 5.3
* New: support for WooCommerce 3.8
* New: Added social sharing for referral link
* Update: Plugin Framework
* Update: Italian language
* Update: Spanish language
* Update: Dutch language
* Tweak: added cache for commission status count
* Tweak: optimized has_unpaid_commissions method
* Tweak: optimized affiliates per_status_count, using wp_cache
* Fix: notices related to missing variables, or unhandled exception return values
* Fix: reset button not appearing on commission page when filtering by status
* Fix: exclude trashed commissions from commission count on the commission page
* Dev: added new filter yith_wcaf_link_generator_generated_url
* Dev: added new filter yith_wcaf_display_symbol
* Dev: added new action yith_wcaf_process_checkout_with_affiliate

= 1.6.4 - Released on 30 October 2019 =

* Update: Plugin framework

= 1.6.3 - Released on 09 August 2019 =

* New: WooCommerce 3.7.0 RC2 support
* Update: internal plugin framework
* Update: Italian language
* Fix: allow copy button from iphone/ipad
* Dev: added new filter yith_wcaf_check_affiliate_val_error
* Dev: added new filter yith_wcaf_dashboard_navigation_menu

= 1.6.2 - Released on 13 June 2019 =

* Update: internal plugin framework
* Tweak: improved uninstall procedure
* Tweak: Changed all doubleval() function to floatval() function

= 1.6.1 - Released on 23 April 2019 =

* Tweak: added rel nofollow to sorting urls
* Update: internal plugin framework

= 1.6.0 - Released on 03 April 2019 =

* New: WooCommerce 3.6.0 RC1 support
* Update: internal plugin framework
* Fix: DB error on backend
* Dev: added new filter yith_wcaf_prepare_items_commissions

= 1.5.1 - Released on 31 January 2019 =

* New: WooCommerce 3.5.3 support
* Tweak: fixed wrong text-domains
* Update: internal plugin framework
* Dev: added filter yith_wcaf_add_affiliate_role

= 1.5.0 - Released on 12 December 2019 =

* New: support to WordPress 5.0
* New: support to WooCommerce 3.5.2
* New: Gutenberg block for yith_wcaf_registration_form shortcode
* New: Gutenberg block for yith_wcaf_affiliate_dashboard shortcode
* New: Gutenberg block for yith_wcaf_link_generator shortcode
* Tweak: updated plugin framework
* Fix: notice in affiliate dashboard
* Fix: notice "trying to retrieve user_login from non-object" on commission table
* Fix: prevent Notice when get_userdata returns a non-object
* Fix: doubled input fields on custom registration form
* Dev: added missing actions on link generator template

= 1.4.1 - Released on 24 October 2018 =

* Tweak: updated plugin framework
* Updated: dutch language
* Fix: minor issues introduced with last update

= 1.4.0 - Released on 03 October 2018 =

* New: support to WooCommerce 3.5-RC1
* New: support to WordPress 4.9.8
* New: updated plugin framework
* New: added new Reject status for affiliates
* New: added commissions Trash
* Fix: affiliate backend creation
* Fix: fixed some queries on various admin views
* Tweak: improved balance calculation
* Dev: added filter get_referral_url filter

= 1.3.1 - Released on 19 July 2018 =

* New: added new fields during affiliate registration
* Fixed: warning occurring when WooCommerce does not send all params to woocommerce_email_order_meta action
* Dev: added filter yith_wcaf_dashboard_affiliate_message

= 1.3.0 - Released on 28 May 2018 =

* New: WooCommerce 3.4 compatibility
* New: WordPress 4.9.6 compatibility
* New: updated plugin-fw
* New: GDPR compliance
* New: admin can now ban Affiliates
* Update: Italian Language
* Update: Spanish language
* Tweak: improved pagination of dashboard sections
* Fix: preventing notice when filtering by date payments

= 1.2.4 - Released on 05 April 2018 =

* New: "yith_wcaf_show_if_affiliate" shortcode
* New: added "process orphan commissions" procedure
* New: added shortcodes for Affiliate Dashboard sections ( [yith_wcaf_show_clicks], [yith_wcaf_show_commissions], [yith_wcaf_show_payments], [yith_wcaf_show_settings] )
* Tweak: remove user_trailingslashit from get_referral_url to improve compatibility
* Tweak: improved user capability handling, now all admin operations require at least manage_woocommerce capability
* Dev: added yith_wcaf_requester_link filter to let third party code change requester link
* Dev: new filter "yith_wcaf_panel_capability" to let third party code change minimum required capability for admin operations
* Dev: added "order_id" param for "yith_wcaf_affiliate_rate" filter

= 1.2.2 - Released on 01 February 2018 =

* New: added WooCommerce 3.3.x support
* New: added WordPress 4.9.2 support
* New: added Dutch translation
* Tweak: added SAMEORIGIN header to Affiliate Dashboard page
* Tweak: fixed error with wrong Affiliate ID when adding new affiliate to database

= 1.2.1 - Released on Nov, 14 - 2017 =

* Fix: added check over user before adding role

= 1.2.0 - Released on 10 November 2017 =

* New: WooCommerce 3.2.x support
* New: new affiliate role
* New: added login form in "Registration form" template
* New: added copy button for generated referral url
* Fix: removed profile panel when customer have permissions lower then shop manager
* Dev: added yith_wcaf_settings_form_start action
* Dev: added yith_wcaf_settings_form action
* Dev: added yith_wcaf_save_affiliate_settings action
* Dev: added yith_wcaf_show_dashboard_links filter to let dev show navigation menu on all affiliates dashboard pages

= 1.1.0 - Released on 04 April 2017 =

* New: WordPress 4.7.3 compatibility
* New: WooCommerce 3.0-RC2 compatibility
* New: Delete bulk action for payments
* Tweak: text domain to yith-woocommerce-affiliates. IMPORTANT: this will delete all previous translations
* Tweak: delete notes while deleting commission
* Fix: delete method for payments
* Fix: commission delete process
* Fix: commission notes delete process
* Dev: added yith_wcaf_affiliate_rate filter to let third party plugin customize affiliate commission rate
* Dev: added yith_wcaf_use_percentage_rates filter to let switch from percentage rate to fixed amount (use it at your own risk, as no control over item total is performed)
* Dev: added yith_wcaf_become_an_affiliate_redirection filter to let third party plugin customize redirection after "Become an Affiliate" butotn is clicked
* Dev: added yith_wcaf_become_affiliate_button_text filter to let third party plugin change Become Affiliate button label
* Dev: added yith_wcaf_payment_email_required filter to let third party plugin to remove payment email from affiliate registration form
* Dev: added yith_wcaf_create_order_commissions filter, to let dev skip commission handling
* Dev: added filters yith_wcaf_before_dashboard_section and yith_wcaf_after_dashboard_section
* Dev: added yith_wcaf_get_current_affiliate_token function to get current affiliate token
* Dev: added yith_wcaf_get_current_affiliate function to get current affiliate object
* Dev: added yith_wcaf_get_current_affiliate_user function to get current affiliate user object

= 1.0.9 - Released on 03 October 2016 =

* Added: function yith_wcaf_get_current_affiliate_token to get current affiliate token
* Added: function yith_wcaf_get_current_affiliate to get current affiliate object
* Added: function yith_wcaf_get_current_affiliate_user to get current affiliate user object
* Added: Delete bulk action for payments
* Added: option to force commissions delete
* Added: filter yith_wcaf_persistent_rate to let dev filter persistent rate
* Tweak: changed text domain to yith-woocommerce-affiliates
* Fixed: Delete method for payments
* Fixed: commissions and notes delete methods

= 1.0.8 - Released on 08 June 2016 =

* Added: support WC 2.6 RC1
* Added: style for #yith_wcaf_order_referral_commissions, #yith_wcaf_payment_affiliate, #yith_wcaf_commission_payments
* Added: per page input in affiliate dashboard
* Tweak: added filter yith_wcaf_is_hosted to filter check over submitted host / server name match in link_generator callback
* Fixed: column ordering anchor in affiliate dashboard

= 1.0.7 - Released on 05 May 2016 =

* Added: WordPress 4.5.x support
* Fixed: removed useless library invocation
* Fixed: generate link shortcode (removed protocol before check for local url)

= 1.0.6 - Released on 05 April 2016 =

* Added filter "yith_wcaf_is_valid_token" to is_valid_token
* Tweak changed EOL to LF
* Tweak: Performance improved with new plugin core 2.0
* Fixed order awaiting payment handling
* Fixed view problems due to new YITH menu page slug
* Fixed generate link shortcode (url parsing improvements)
* Fixed affiliate research
* Fixed plugin-fw loading

= 1.0.5 - Released on 16 October 2015 =

* Added: Option to prevent referral cookie to expire
* Tweak: Increased expire seconds limit
* Tweak: Changed disabled attribute in readonly attribute for link-generator template
* Fixed: Commissions/Payment status now translatable from .po files
* Fixed: Fatal error occurring sometimes when using YOAST on backend

= 1.0.4 - Released on 13 August 2015 =

* Added: Compatibility with WC 2.4.2
* Tweak: Added missing text domain on link-generator template (thanks to dabodude)
* Tweak: Updated internal plugin-fw

= 1.0.3 - Released on 05 August 2015 =

* Fixed: minor bugs

= 1.0.2 - Released on 03 April 2015 =

* Tweak: Improved older PHP versions compatibility (removed dynamic class invocation)

= 1.0.1 - Released on 31 July 2015 =

* Fixed: fatal error for PHP version older then 5.5

= 1.0.0 - Released on 30 July 2015 =

* Initial release

== Suggestions ==

If you have suggestions about how to improve YITH WooCommerce Affiliates, you can [write us](mailto:plugins@yithemes.com "Your Inspiration Themes") so we can bundle them into YITH WooCommerce Affiliates.

== Translators ==

= Available Languages =
* English (Default)
* Italian (Italy)
* Spanish (Spain)
* Dutch (Netherlands)

Need to translate this plugin into your own language? You can contribute to its translation from [this page](https://translate.wordpress.org/projects/wp-plugins/yith-woocommerce-affiliates "Translating WordPress").
Your help is precious! Thanks
