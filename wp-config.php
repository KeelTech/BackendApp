<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'u561901675_getkeel' );

/** MySQL database username */
define( 'DB_USER', 'u561901675_getkeel' );

/** MySQL database password */
define( 'DB_PASSWORD', 'Ws@12345' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );

/** Database Charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The Database Collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );


/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'igha(yeW*DBs,,$Qu~B^k]0 w>dR_nf:~5!A7_jMB]_?1KCy=W{ON%tsL3P&Rv+A' );
define( 'SECURE_AUTH_KEY',  'c!))v:g5i:s5jj%uiKcd#b[nuoHIN8F?EK;y%A}0O5FzFM46rC4_T.*[oV?Xe!~D' );
define( 'LOGGED_IN_KEY',    '*8q-xC?n6cUhMFb`H),,F/N{_TzCD*-x5q]ixqU~oTXDe!H/tR:HVTZ~Tek>peAQ' );
define( 'NONCE_KEY',        'Fm$ZqIw>y-tC#]A#+op&jIlz1u+kg!F;JR0YldsoeLZ,ga5Ag47723:-ml7E#{9i' );
define( 'AUTH_SALT',        'uWSzyoHFY+_@DU/*(`ysk^P7YK>Ou?:x_DGJSC-Bfgu6It[IwlExaX c9Yi3l7J<' );
define( 'SECURE_AUTH_SALT', 'LvPvsi,{}u#V0O+PPyk/D(dwNvA?9t__|JiFszulg<$;b1m]Ek3p$AzwsD(X(cwT' );
define( 'LOGGED_IN_SALT',   'Zcl2>S`WXIx-P?^z[r[Rg8j1ge8NBzGQx1R@6Em,WbM~%`@cFK!u2X9Hz9aJQRDb' );
define( 'NONCE_SALT',       'T(8Av~&R lTkC<O_Y2Ga*xFGw{C)d ;DG[-ZfW0&!{<U-vZjMzfd1,iO][:}p%}?' );

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'FS_METHOD', 'direct' );
define( 'WP_DEBUG', false );

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';

@ini_set( 'upload_max_filesize' , '256M' );
@ini_set( 'post_max_size', '256M');
@ini_set( 'memory_limit', '256M' );
@ini_set( 'max_execution_time', '300' );
@ini_set( 'max_input_time', '300' );