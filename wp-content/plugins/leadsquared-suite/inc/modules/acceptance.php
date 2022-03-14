<?php
 $args = wp_parse_args( $args, array() );
	$type = 'acceptance';
	$json = getMetadata();
		$decode_json = json_decode($json, TRUE);
		$args = wp_parse_args( $args, array() );

?>
<div class="control-box">
<fieldset>


<table class="form-table">
<tbody>
	<tr>
	<th scope="row"><label for="<?php echo esc_attr( $args['content'] . '-name' ); ?>"><?php echo esc_html( __( 'Name', 'contact-form-7' ) ); ?></label></th>
	<td><select name="leadsquared-field-name-ys" class="tg-name oneline" id="leadsquared-field-name-ys">
	<option>--</option>
							<?php 
							$number = lsq_search($decode_json, 'DataType', 'Boolean');
							if($number) { $data_type = array(); foreach($number as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
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
		<label><input type="checkbox" name="default:on" class="option" /> <?php echo esc_html( __( 'Make this checkbox checked by default', 'contact-form-7' ) ); ?></label><br />
		<label><input type="checkbox" name="invert" class="option" /> <?php echo esc_html( __( 'Make this work inversely', 'contact-form-7' ) ); ?></label>
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
	<input type="text" name="<?php echo $type; ?>" class="tag code" readonly="readonly" onfocus="this.select()" />

	<div class="submitbox">
	<input type="button" class="button button-primary insert-tag" value="<?php echo esc_attr( __( 'Insert Tag', 'contact-form-7' ) ); ?>" />
	</div>
</div>
<script>
(function($){
    'use strict';

    $(document).ready(function() {
		
        var $lsqfn = $('#leadsquared-field-name-ys');
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