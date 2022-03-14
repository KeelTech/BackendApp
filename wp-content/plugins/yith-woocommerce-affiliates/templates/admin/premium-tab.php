<?php
/**
 * Premium Tab
 *
 * @author Your Inspiration Themes
 * @package YITH WooCommerce Affiliates
 * @version 1.0.0
 */

/*
 * This file belongs to the YIT Framework.
 *
 * This source file is subject to the GNU GENERAL PUBLIC LICENSE (GPL 3.0)
 * that is bundled with this package in the file LICENSE.txt.
 * It is also available through the world-wide-web at this URL:
 * http://www.gnu.org/licenses/gpl-3.0.txt
 */

if ( ! defined( 'YITH_WCAF' ) ) {
	exit;
} // Exit if accessed directly
?>

<style>
.section{
    margin-left: -20px;
    margin-right: -20px;
    font-family: "Raleway",san-serif;
}
.section h1{
    text-align: center;
    text-transform: uppercase;
    color: #808a97;
    font-size: 35px;
    font-weight: 700;
    line-height: normal;
    display: inline-block;
    width: 100%;
    margin: 50px 0 0;
}
.section ul{
    list-style-type: disc;
    padding-left: 15px;
}
.section:nth-child(even){
    background-color: #fff;
}
.section:nth-child(odd){
    background-color: #f1f1f1!important;
}
.section .section-title img{
    display: table-cell;
    vertical-align: middle;
    width: auto;
    margin-right: 15px;
}
.section h2,
.section h3 {
    display: inline-block;
    vertical-align: middle;
    padding: 0;
    font-size: 24px;
    font-weight: 700;
    color: #808a97;
    text-transform: uppercase;
}

.section .section-title h2{
    display: table-cell;
    vertical-align: middle;
    line-height: 25px;
}

.section-title{
    display: table;
}

.section h3 {
    font-size: 14px;
    line-height: 28px;
    margin-bottom: 0;
    display: block;
}

.section p{
    font-size: 13px;
    margin: 25px 0;
}
.section ul li{
    margin-bottom: 4px;
}
.landing-container{
    max-width: 750px;
    margin-left: auto;
    margin-right: auto;
    padding: 50px 0 30px;
}
.landing-container:after{
    display: block;
    clear: both;
    content: '';
}
.landing-container .col-1,
.landing-container .col-2{
    float: left;
    box-sizing: border-box;
    padding: 0 15px;
}
.landing-container .col-1 img{
    width: 100%;
}
.landing-container .col-1{
    width: 55%;
}
.landing-container .col-2{
    width: 45%;
}
.premium-cta{
    background-color: #808a97;
    color: #fff;
    border-radius: 6px;
    padding: 20px 15px;
}
.premium-cta:after{
    content: '';
    display: block;
    clear: both;
}
.premium-cta p{
    margin: 7px 0;
    font-size: 14px;
    font-weight: 500;
    display: inline-block;
    width: 60%;
}
.premium-cta a.button{
    border-radius: 6px;
    height: 60px;
    float: right;
    background: url(<?php echo YITH_WCAF_URL?>assets/images/upgrade.png) #ff643f no-repeat 13px 13px;
    border-color: #ff643f;
    box-shadow: none;
    outline: none;
    color: #fff;
    position: relative;
    padding: 9px 50px 9px 70px;
}
.premium-cta a.button:hover,
.premium-cta a.button:active,
.premium-cta a.button:focus{
    color: #fff;
    background: url(<?php echo YITH_WCAF_URL?>assets/images/upgrade.png) #971d00 no-repeat 13px 13px;
    border-color: #971d00;
    box-shadow: none;
    outline: none;
}
.premium-cta a.button:focus{
    top: 1px;
}
.premium-cta a.button span{
    line-height: 13px;
}
.premium-cta a.button .highlight{
    display: block;
    font-size: 20px;
    font-weight: 700;
    line-height: 20px;
}
.premium-cta .highlight{
    text-transform: uppercase;
    background: none;
    font-weight: 800;
    color: #fff;
}

.section.one{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/01-bg.png) no-repeat #fff; background-position: 85% 75%
}
.section.two{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/02-bg.png) no-repeat #fff; background-position: 15% 75%
}
.section.three{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/03-bg.png) no-repeat #fff; background-position: 85% 75%
}
.section.four{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/04-bg.png) no-repeat #fff; background-position: 15% 75%
}
.section.five{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/05-bg.png) no-repeat #fff; background-position: 85% 75%
}
.section.six{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/06-bg.png) no-repeat #fff; background-position: 15% 75%
}
.section.seven{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/07-bg.png) no-repeat #fff; background-position: 85% 75%
}
.section.eight{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/08-bg.png) no-repeat #fff; background-position: 15% 75%
}
.section.nine{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/09-bg.png) no-repeat #fff; background-position: 85% 75%
}
.section.ten{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/10-bg.png) no-repeat #fff; background-position: 15% 75%
}
.section.eleven{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/11-bg.png) no-repeat #fff; background-position: 85% 75%
}
.section.twelve{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/12-bg.png) no-repeat #fff; background-position: 15% 75%
}
.section.therteen{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/13-bg.png) no-repeat #fff; background-position: 85% 75%
}
.section.forteen{
    background: url(<?php echo YITH_WCAF_URL?>assets/images/14-bg.png) no-repeat #fff; background-position: 15% 75%
}

@media (max-width: 768px) {
    .section{margin: 0}
    .premium-cta p{
        width: 100%;
    }
    .premium-cta{
        text-align: center;
    }
    .premium-cta a.button{
        float: none;
    }
}

@media (max-width: 480px){
    .wrap{
        margin-right: 0;
    }
    .section{
        margin: 0;
    }
    .landing-container .col-1,
    .landing-container .col-2{
        width: 100%;
        padding: 0 15px;
    }
    .section-odd .col-1 {
        float: left;
        margin-right: -100%;
    }
    .section-odd .col-2 {
        float: right;
        margin-top: 65%;
    }
}

@media (max-width: 320px){
    .premium-cta a.button{
        padding: 9px 20px 9px 70px;
    }

    .section .section-title img{
        display: none;
    }
}
</style>
<div class="landing">
    <div class="section section-cta section-odd">
        <div class="landing-container">
            <div class="premium-cta">
                <p>
                    <?php echo sprintf( __('Upgrade to %1$spremium version%2$s of %1$sYITH WooCommerce Affiliates%2$s to benefit from all features!','yith-woocommerce-affiliates'),'<span class="highlight">','</span>' );?>
                </p>
                <a href="<?php echo $this->get_premium_landing_uri() ?>" target="_blank" class="premium-cta-button button btn">
                    <span class="highlight"><?php _e('UPGRADE','yith-woocommerce-affiliates');?></span>
                    <span><?php _e('to the premium version','yith-woocommerce-affiliates');?></span>
                </a>
            </div>
        </div>
    </div>
    <div class="one section section-even clear">
        <h1><?php _e('Premium Features','yith-woocommerce-affiliates');?></h1>
        <div class="landing-container">
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/01.png" alt="<?php _e( 'PayPal','yith-woocommerce-affiliates') ?>" />
            </div>
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/01-icon.png" alt="icon 01"/>
                    <h2><?php _e('PayPal','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf(__('All professionalism and advantages that PayPal puts at your disposal to offer you the best solution for %1$spayments%2$s of commissions owed to your affiliate users.%3$sPayPal is one of the most common payment methods in the market and a system able to offer you higher guarantees, you cannot do without it!', 'yith-woocommerce-affiliates'), '<b>', '</b>','<br>');?>
                </p>
            </div>
        </div>
    </div>
    <div class="two section section-odd clear">
        <div class="landing-container">
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/02-icon.png" alt="icon 02" />
                    <h2><?php _e('Automatic payment','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf(__('It\'s time to automate payment system for commissions in your store: the more the traffic in your shop, the more the commissions to pay to your affiliates. You might not find always the time to do that and you might, then, risk to be late with payments and not respect deadlines. ', 'yith-woocommerce-affiliates'), '<b>', '</b>');?>
                </p>
                <p>
                    <?php echo sprintf(__('Choose either to pay your affiliates each time a %1$snew commission%2$s is due to them, or to pay the balance on one %1$sspecific day%2$s of the month or to send the amount owed only when a specific commission amount %1$sthreshold%2$s is reached.', 'yith-woocommerce-affiliates'), '<b>', '</b>');?>
                </p>
            </div>
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/02.png" alt="<?php _e( 'Automatic payment','yith-woocommerce-affiliates') ?>" />
            </div>
        </div>
    </div>
    <div class="three section section-even clear">
        <div class="landing-container">
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/03.png" alt="<?php _e( 'Click Info','yith-woocommerce-affiliates') ?>" />
            </div>
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/03-icon.png" alt="icon 03" />
                    <h2><?php _e( 'Click info','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf(__('For any new visit coming from an %1$saffiliate%2$s link, the system stores related information, such as referrer name, visited page, date and possible order ID associated. In the latter case, it stores also conversion time, that is the time passed before a click converts into an order.', 'yith-woocommerce-affiliates'), '<b>', '</b>');?>
                </p>
            </div>
        </div>
    </div>
    <div class="four section section-odd clear">
        <div class="landing-container">
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/04-icon.png" alt="icon 04" />
                    <h2><?php _e('Commission rate','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf(__('Set a basic commission rate for your entire shop, but do not limit to this only!%3$sEnter a different commission according to user or purchased product. In a quick and easy way, so, you will  be able to create a %1$scommission hierarchy%2$s according to your needs and your business methods.', 'yith-woocommerce-affiliates'), '<b>', '</b>','<br>');?>
                </p>
            </div>
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/04.png" alt="<?php _e( 'Commission rate','yith-woocommerce-affiliates') ?>" />
            </div>
        </div>
    </div>
    <div class="five section section-even clear">
        <div class="landing-container">
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/05.png" alt="<?php _e( 'Permanent association','yith-woocommerce-affiliates') ?>" />
            </div>
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/05-icon.png" alt="icon 05" />
                    <h2><?php _e('Permanent association','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __( 'A special way to encourage affiliates to take more and more customers to your site. After the first purchase from your affiliate link, all following orders will generate a %1$scommission%2$s earning for the associated affiliate.','yith-woocommerce-affiliates' ),'<b>','</b>' ) ?>
                </p>
                <p>
                    <?php echo sprintf( __( 'This feature, that you can either enable or not, might be a powerful tool for drawing the attention of all those interested in an affiliation programme.','yith-woocommerce-affiliates' ),'<b>','</b>') ?>
                </p>
            </div>
        </div>
    </div>
    <div class="six section section-odd clear">
        <div class="landing-container">
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/06-icon.png" alt="icon 06" />
                    <h2><?php _e('Affiliate history','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('As easy as useful for those like you who need to track all moves on your site.All orders linked to affiliates show an %1$s"affiliation history"%2$s, a comprehensive chronological list with all affiliates who have contributed to generate visits from that user in your site.','yith-woocommerce-affiliates'),'<b>','</b>','<br>'); ?>
                </p>
            </div>
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/06.png" alt="<?php _e( 'Mobile devices','yith-woocommerce-affiliates') ?>" />
            </div>
        </div>
    </div>
    <div class="seven section section-even clear">
        <div class="landing-container">
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/07.png" alt="<?php _e( 'Automatic approval','yith-woocommerce-affiliates') ?>" />
            </div>
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/07-icon.png" alt="icon 07" />
                    <h2><?php _e('Automatic approval of new affiliates','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('If you do not want to waste your time approving all users who apply for becoming affilitates in your shop, do not worry, with the premium version you will just have enable an option and it\'s done: %1$sany new affiliate%2$s will be immediately ready to advertise your products!','yith-woocommerce-affiliates'),'<b>','</b>'); ?>
                </p>
            </div>
        </div>
    </div>
    <div class="eight section section-odd clear">
        <div class="landing-container">
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/08-icon.png" alt="icon 08" />
                    <h2><?php _e('Click duration','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('You might need to make some %1$sstatistics%2$s about %1$sactivities%2$s connected to all affiliates in your site and probably also the number of visits generated by each of them. In order not to distort these data, you can set the number of seconds that have to pass before a visit form the same user can be counted as a new click in click logs.','yith-woocommerce-affiliates'),'<b>','</b>','<br>'); ?>
                </p>
            </div>
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/08.png" alt="<?php _e( 'Click duration','yith-woocommerce-affiliates') ?>" />
            </div>
        </div>
    </div>
    <div class="nine section section-even clear">
        <div class="landing-container">
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/09.png" alt="<?php _e( 'Report','yith-woocommerce-affiliates') ?>" />
            </div>
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/09-icon.png" alt="icon 09" />
                    <h2><?php _e('Report','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('An entire section devoted to statistics about commissions and conversions generated for each visit. A global area with all data collected from general actions from users and another more detailed one, that allows you to read details of each single product and verify the number of %1$svisits%2$s generated, earnings coming from %1$saffiliation%2$s operations and conversion percentage.','yith-woocommerce-affiliates'),'<b>','</b>'); ?>
                </p>
            </div>
        </div>
    </div>
    <div class="ten section section-odd clear">
        <div class="landing-container">
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/10-icon.png" alt="icon 10" />
                    <h2><?php _e('Notification email','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('Enjoy the benefits of notification emails that the plugin allows you to get in order to keep both administratore and users (affiliate and not) always updated.%3$sAny new %1$saffiliation request%2$s or %1$scommission payment%2$s will be notified via email in a dynamic site like yours!','yith-woocommerce-affiliates'),'<b>','</b>','<br>'); ?>
                </p>
            </div>
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/10.png" alt="<?php _e( 'Notification email','yith-woocommerce-affiliates') ?>" />
            </div>
        </div>
    </div>
    <div class="eleven section section-even clear">
        <div class="landing-container">
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/11.png" alt="<?php _e( 'Report','yith-woocommerce-affiliates') ?>" />
            </div>
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/11-icon.png" alt="icon 09" />
                    <h2><?php _e('Affiliation code','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('User is usually associated to the affiliate thanks to an affiliation code which has been inserted in the url that led user to your site. In this case, affiliation is automatic. %1$s In case this behavior doesn\'t satisfy your needs, you can request the insertion of the affiliation code through the specific form in "Checkout" page.','yith-woocommerce-affiliates'),'<br>'); ?>
                </p>
            </div>
        </div>
    </div>
    <div class="twelve section section-odd clear">
        <div class="landing-container">
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/12-icon.png" alt="icon 10" />
                    <h2><?php _e('Delete cookie','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('The user reached your site through an affiliation. %1$sFor how long will his/her purchases generate commissions for the affiliate?%2$s You can choose by setting a deadline or by making sure the affiliation will be deleted after the first purchase.','yith-woocommerce-affiliates'),'<b>','</b>'); ?>
                </p>
            </div>
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/12.png" alt="<?php _e( 'Notification email','yith-woocommerce-affiliates') ?>" />
            </div>
        </div>
    </div>
    <div class="therteen section section-even clear">
        <div class="landing-container">
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/13.png" />
            </div>
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/13-icon.png" />
                    <h2><?php _e('Add and remove affiliates from an order','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('%1$sSelect the order and associate it with one of your store affiliates.%2$s %3$sNow you can do this by simply accessing your admin panel.','yith-woocommerce-affiliates'),'<b>','</b>','<br>'); ?>
                </p>
                <p>
                    <?php _e('The same goes for referrals already linked to an order: commissions will be calculated automatically as soon as you save.','yith-woocommerce-affiliates'); ?>
                </p>
            </div>
        </div>
    </div>
    <div class="forteen section section-odd clear">
        <div class="landing-container">
            <div class="col-2">
                <div class="section-title">
                    <img src="<?php echo YITH_WCAF_URL?>assets/images/14-icon.png" alt="icon 14" />
                    <h2><?php _e('Let affiliates request payments','yith-woocommerce-affiliates');?></h2>
                </div>
                <p>
                    <?php echo sprintf( __('Affiliates can now request a withdrawal of their commissions. Affiliates will be able to request withdrawals, upload invoices for their withdrawals and generate new invoices for their withdrawal requests. By simply enabling the option in the backend, a new menu label will appear in the affilates dasboard.','yith-woocommerce-affiliates'),'<b>','</b>'); ?>
                </p>
            </div>
            <div class="col-1">
                <img src="<?php echo YITH_WCAF_URL?>assets/images/14.png" alt="<?php _e( 'Withdraw','yith-woocommerce-affiliates') ?>" />
            </div>
        </div>
    </div>
    <div class="section section-cta section-odd">
        <div class="landing-container">
            <div class="premium-cta">
                <p>
                    <?php echo sprintf( __('Upgrade to %1$spremium version%2$s of %1$sYITH WooCommerce Affiliates%2$s to benefit from all features!','yith-woocommerce-affiliates'),'<span class="highlight">','</span>' );?>
                </p>
                <a href="<?php echo $this->get_premium_landing_uri() ?>" target="_blank" class="premium-cta-button button btn">
                    <span class="highlight"><?php _e('UPGRADE','yith-woocommerce-affiliates');?></span>
                    <span><?php _e('to the premium version','yith-woocommerce-affiliates');?></span>
                </a>
            </div>
        </div>
    </div>
</div>
