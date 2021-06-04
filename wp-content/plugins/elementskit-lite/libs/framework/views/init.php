<?php

$sections = [
    'dashboard' => [
        'title' => esc_html__('Dashboard', 'elementskit-lite'),
        'sub-title' => esc_html__('General info', 'elementskit-lite'),
        'icon' => 'icon icon-home',
        // 'view_path' => 'some path to the view file'
    ],
    'elements' => [
        'title' => esc_html__('Elements', 'elementskit-lite'),
        'sub-title' => esc_html__('Enable disable widgets', 'elementskit-lite'),
        'icon' => 'icon icon-magic-wand',
    ],
    'modules' => [
        'title' => esc_html__('Modules', 'elementskit-lite'),
        'sub-title' => esc_html__('Enable disable modules', 'elementskit-lite'),
        'icon' => 'icon icon-settings-2',
    ],
    'userdata' => [
        'title' => esc_html__('User Data', 'elementskit-lite'),
        'sub-title' => esc_html__('Data for fb, mailchimp etc', 'elementskit-lite'),
        'icon' => 'icon icon-settings1',
    ],
];

$sections = apply_filters('elementskit/admin/sections/list', $sections);

?>
<div class="ekit-wid-con">
    <div class="ekit_container">
        <form action="" method="POST" id="ekit-admin-settings-form">
            <?php 
                if(isset($_GET['onboard-steps']) && $_GET['onboard-steps'] == 'first-time'){
                    include 'layout-onboard.php'; 
                }else{
                    include 'layout-settings.php';
                }
            ?>
        </form>
    </div>
</div>