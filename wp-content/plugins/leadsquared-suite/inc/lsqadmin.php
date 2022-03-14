<?php
$lsq_modules = get_option("leadsquared_modules");
if (isset($_GET['activate'])) 
{
	if($_GET['activate'] == "lsqform")
		$lsq_modules['lsqform'] = '1';
	if($_GET['activate'] == "lsqts")
		$lsq_modules['lsqts'] = '1';
	if($_GET['activate'] == "cf72lsq")
		$lsq_modules['cf72lsq'] = '1';
	if($_GET['activate'] == "lsqc2l")
		$lsq_modules['lsqc2l'] = '1';
	update_option( "leadsquared_modules", $lsq_modules );
}
if (isset($_GET['deactivate'])) 
{
	if($_GET['deactivate'] == "lsqform")
		$lsq_modules['lsqform'] = '0';
	if($_GET['deactivate'] == "lsqts")
		$lsq_modules['lsqts'] = '0';
	if($_GET['deactivate'] == "cf72lsq")
		$lsq_modules['cf72lsq'] = '0';
	if($_GET['deactivate'] == "lsqc2l")
		$lsq_modules['lsqc2l'] = '0';
	update_option( "leadsquared_modules", $lsq_modules );

}
$modules = get_option("leadsquared_modules");
?>
<div class="lsq-herp" style="background:url(<?php  print LSQFORM_PLUGIN_URL ?>images/bg.jpg);height:300px;width:100%;margin-left:-20px;padding:10px;">
	<div class="lsq-logo" style="width: 193px;margin: auto;margin-top: 25px;"><img src="<?php  print LSQFORM_PLUGIN_URL ?>images/logo.png" style="width: 165px;margin-top: 20px;margin-bottom: -5px;"/></div>
	
	<div class="lsq-headlines" style="text-align:center;margin-top:40px;">
		<h1 style="color:#fff;color:#fff;font-weight: 500;font-size: 36px;line-height:36px;">LeadSquared Wordpress Suite</h1>
		<p  style="color:#fff;font-size: 16px;    margin-top: -15px;">Reach the full potential of lead capture with Leadsquared's WordPress integration</p>
	</div>
</div>
<div class="triangle-down"></div>
<div class="wrap" id="leadsquared-home">
	
	<div class="lsq-features-wrap">
		<div class="lsq-features-plugins">
			<div class="lsq-plugins">
				<h3>LeadSquared Form</h3>
				<p>Your leadsquared form on your wordpress site</p>
				<?php if($modules['lsqform'] == '1') { ?>
				<a href="<?php menu_page_url( 'leadsquared-wordpress-suit');?>&deactivate=lsqform" class="button">Deactivate</a>
				<?php } else { ?> 
				<a href="<?php menu_page_url( 'leadsquared-wordpress-suit');?>&activate=lsqform" class="button button-primary button-large">Activate</a>
				<?php }?>
				
			</div>
			<div class="lsq-plugins">
				<h3>LeadSquared Tracking Script</h3>
				<p>Track user active of your website on leadsquared</p>
				<?php if($modules['lsqts'] == '1') { ?>
				<a href="<?php menu_page_url( 'leadsquared-wordpress-suit');?>&deactivate=lsqts" class="button">Deactivate</a>
				<?php } else { ?> 
				<a href="<?php menu_page_url( 'leadsquared-wordpress-suit');?>&activate=lsqts" class="button button-primary button-large">Activate</a>
				<?php }?>
			</div>
			<div class="lsq-plugins">
				<h3>Comments to LeadSquared</h3>
				<p>Track user active of your website on leadsquared</p>
				<?php if($modules['lsqc2l'] == '1') { ?>
				<a href="<?php menu_page_url( 'leadsquared-wordpress-suit');?>&deactivate=lsqc2l" class="button">Deactivate</a>
				<?php } else { ?> 
				<a href="<?php menu_page_url( 'leadsquared-wordpress-suit');?>&activate=lsqc2l" class="button button-primary button-large">Activate</a>
				<?php }?>
			</div>
			<div class="lsq-plugins">
				<h3>Contact Form 7 Integration</h3>
				<p>Contact form 7 lead lead to Leadsquared</p>
				<?php if($modules['cf72lsq'] == '1') { ?>
				<a href="<?php menu_page_url( 'leadsquared-wordpress-suit');?>&deactivate=cf72lsq" class="button">Deactivate</a>
				<?php } else { ?> 
				<a href="<?php menu_page_url( 'leadsquared-wordpress-suit');?>&activate=cf72lsq" class="button button-primary button-large">Activate</a>
				<?php }?>
			</div>
			<div class="clear"></div>
		</div>
	</div>
<style>
.lsq-features-wrap{
	padding:30px;
}
.lsq-plugins{
	display: block;
    padding: 0.71429em 1.07143em 1em;
    text-align: left;
    border: 1px solid #dae0e2;
    background: #fff;
    box-shadow: 0 0 0 rgba(0,0,0,0.03);
    transition: opacity 2s ease-in;
	position: relative;
    float: left;
    margin: 0 5px 10px;
    width: 250px;
    transition: all .2s ease-in-out;
}
.lsq-features-plugins{
	max-width:870px;
	margin:auto;
}
.lsq-plugins h3	{
	cursor: pointer;
    margin: 0 0 0.5em;
    color: #1a8dba;
    font-size: 1.14286em;
    line-height: 1.4em;
    font-weight: 700;
	}
.triangle-down {
    width: 10%;
    padding-left:10%;
    padding-top: 0%;
    overflow: hidden;
	margin:auto;
}
.triangle-down:after {
    content: "";
    display: block;
    width: 0;
    height: 0;
    margin-left:-500px;
    margin-top:-500px;
    
    border-left: 500px solid transparent;
    border-right: 500px solid transparent;
    border-top: 520px solid #009BFD;
}

</style>	
</div>