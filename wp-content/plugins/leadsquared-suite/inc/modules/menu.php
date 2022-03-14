<?php
		$json = getMetadata();
		$decode_json = json_decode($json, TRUE);
		$args = wp_parse_args( $args, array() );
?>
<div class="control-box">
<fieldset>
<table class="form-table">
<tbody>
	<tr>
	<th scope="row"><?php echo esc_html( __( 'Field type', 'contact-form-7' ) ); ?></th>
	<td>
		<fieldset>
		<legend class="screen-reader-text"><?php echo esc_html( __( 'Field type', 'contact-form-7' ) ); ?></legend>
		<label><input type="checkbox" name="required" /> <?php echo esc_html( __( 'Required field', 'contact-form-7' ) ); ?></label>
		</fieldset>
	</td>
	</tr>

	<tr>
	<th scope="row"><label for="<?php echo esc_attr( $args['content'] . '-name' ); ?>"><?php echo esc_html( __( 'Name', 'contact-form-7' ) ); ?></label></th>
	<td><select name="leadsquared-field-name-menu" class="tg-name oneline" id="leadsquared-field-name-menu">
	<option>--</option>
							<?php 
							$number = lsq_search($decode_json, 'DataType', 'Select');
							if($number) { $data_type = array(); foreach($number as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}

							$number = lsq_search($decode_json, 'DataType', 'MultiSelect');
							if($number) { $data_type = array(); foreach($number as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-multi-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td>
	</tr>

	<tr>
	<th scope="row"><?php echo esc_html( __( 'Options', 'contact-form-7' ) ); ?></th>
	<td>
		<fieldset>
		<legend class="screen-reader-text"><?php echo esc_html( __( 'Options', 'contact-form-7' ) ); ?></legend>
		<textarea name="values" class="values" id="<?php echo esc_attr( $args['content'] . '-values' ); ?>"></textarea>
		<label for="<?php echo esc_attr( $args['content'] . '-values' ); ?>"><span class="description"><?php echo esc_html( __( "One option per line.", 'contact-form-7' ) ); ?></span></label><br />
		<label><input type="checkbox" name="multiple" class="option" /> <?php echo esc_html( __( 'Allow multiple selections', 'contact-form-7' ) ); ?></label><br />
		<label><input type="checkbox" name="include_blank" class="option" /> <?php echo esc_html( __( 'Insert a blank item as the first option', 'contact-form-7' ) ); ?></label>
		</fieldset>
	</td>
	</tr>

	<tr>
	<th scope="row"><label for="<?php echo esc_attr( $args['content'] . '-id' ); ?>"><?php echo esc_html( __( 'Id attribute', 'contact-form-7' ) ); ?></label></th>
	<td><input type="text" name="id" class="idvalue oneline option" id="<?php echo esc_attr( $args['content'] . '-id' ); ?>" /></td>
	</tr>

	<tr>
	<th scope="row"><label for="<?php echo esc_attr( $args['content'] . '-class' ); ?>"><?php echo esc_html( __( 'Class attribute', 'contact-form-7' ) ); ?></label></th>
	<td><input type="text" name="class" class="classvalue oneline option" id="<?php echo esc_attr( $args['content'] . '-class' ); ?>" /></td>
	</tr>

</tbody>
</table>
</fieldset>
</div>

<div class="insert-box">
	<input type="text" name="select" class="tag code" readonly="readonly" onfocus="this.select()" />

	<div class="submitbox">
	<input type="button" class="button button-primary insert-tag" value="<?php echo esc_attr( __( 'Insert Tag', 'contact-form-7' ) ); ?>" />
	</div>

	<br class="clear" />

	<p class="description mail-tag"><label for="<?php echo esc_attr( $args['content'] . '-mailtag' ); ?>"><?php echo sprintf( esc_html( __( "To use the value input through this field in a mail field, you need to insert the corresponding mail-tag (%s) into the field on the Mail tab.", 'contact-form-7' ) ), '<strong><span class="mail-tag"></span></strong>' ); ?><input type="text" class="mail-tag code hidden" readonly="readonly" id="<?php echo esc_attr( $args['content'] . '-mailtag' ); ?>" /></label></p>
</div>
<script>
(function($){
    'use strict';

    $(document).ready(function() {
		
		
		
        var $lsqfn = $('#leadsquared-field-name-menu');
        var $form = $lsqfn.closest('form');
        var $tagGenerator = $form.find('.insert-box > input:not(.hidden)');
	
        $form.change(function() {
            var tag = $tagGenerator.val();
            var selectedField = $lsqfn.val();

            // Update the generated tag
            if ( selectedField != '0' ) {
                // Form Tag
                if ( tag.match(/(\s+leadsquared[a-z-]+)/) ) {
                    $tagGenerator.val(tag.replace(/(\s+leadsquared[a-z-]+)/, selectedField));
                } else {
                    $tagGenerator.val(tag.replace(/(^\[\w+\*?)/, '$1 ' + selectedField));
                }
                // Mail tag
                $form.find('#tag-generator-panel-leadsquared-mailtag').val('[' + selectedField + ']');
                $form.find('span.mail-tag').text('[' + selectedField + ']');
            } else {
                $tagGenerator.val(tag.replace(/(\s+leadsquared[a-z-]+)/, ''));
                $form.find('#tag-generator-panel-leadsquared-mailtag').val('[]');
                $form.find('span.mail-tag').text('[]');
            }
			

            
        });
    });
})(jQuery);
</script>