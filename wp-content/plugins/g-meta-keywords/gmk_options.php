<?php
	function gmk_reg_set() {
		add_option( 'post_type', '' );
		register_setting( 'gmk_group', 'post_type', 'gmk_callback' );
	}

	add_action( 'admin_init', 'gmk_reg_set' );

	function gmk_register_options_page() {
		add_menu_page( 'G Meta Keywords', 'G Meta Keywords', 'manage_options', 'g-meta-keywords', 'gmk_options_page', 'dashicons-tag' );
	}

	add_action( 'admin_menu', 'gmk_register_options_page' );

	function gmk_options_page() {
		wp_enqueue_style( 'gmk', plugins_url( '/css/gmk.css', __FILE__ ), false, 1, 'all' );
		wp_enqueue_style( 'google-fonts', 'https://fonts.googleapis.com/css?family=Barlow+Semi+Condensed:300,500,700|Pacifico|Roboto:300,500,700&amp;subset=latin-ext', false, 1, 'all' );
		?>

		<div class="admin-panel clearfix">
			<div class="slidebar">
				<div class="logo">
					<a href=""></a>
				</div>
				<ul>
					<li class="active-menu"><?php _e( 'General Settings', 'g-meta-keywords' ); ?></li>
				</ul>
			</div>
			<div class="main">
				<ul class="topbar clearfix">
					<li><?php _e( 'Release', 'g-meta-keywords' ); ?>: 1.3</li>
				</ul>
				<div class="mainContent clearfix">
					<form method="post" action="options.php">
						<?php settings_fields( 'gmk_group' ); ?>
						<div id="general-settings">
							<h2 class="header"><?php _e( 'General Settings', 'g-meta-keywords' ); ?></h2>
							<p><?php _e( 'On this page, you can manage all settings for G Meta Keywords (GMK) plugin.', 'g-meta-keywords' ); ?></p>
							<div class="widget-box">
								<h4><?php _e( 'Allow "Post Type"', 'g-meta-keywords' ); ?></h4>
								<p style="margin-left:0;"><?php _e( 'In some themes, there might be custom "Post Type"s created by theme developers. GMK plugin might not shown on those custom post type pages. In this case you have to add post types to the textbox below. You can write one "Post Type" per line.', 'g-meta-keywords' ); ?></p>
								<textarea style="padding:15px;" name="post_type" id="post_type" cols="30" placeholder="<?php _e( 'Ex: services', 'g-meta-keywords' ); ?>" rows="10"><?= get_option( 'post_type' ) ?></textarea>
								<button type="submit" id="submit" class="submit" name="submit"><?php _e( 'Save Settings', 'g-meta-keywords' ); ?></button>
							</div>
						</div>
					</form>
				</div>
				<ul class="statusbar">
					<li class="logout">
						<a href="https://sinanyorulmaz.com" target="_blank"><?php _e( 'Developer', 'g-meta-keywords' ); ?></a>
					</li>
					<li class="profiles-setting">
						<a href="https://demo.grana.com.tr/web/wordpress/plugin/g-meta-keywords/" target="_blank"><?php _e( 'About', 'g-meta-keywords' ); ?></a>
					</li>
				</ul>
			</div>
		</div>
		<?php
	}

?>