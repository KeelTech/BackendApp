<?php	
$json = getMetadata();
$decode_json = json_decode($json, TRUE);
?>
	<div id="wpcf7-tg-pane-leadsquared-text" class="hidden">
		<form action="">
			<table>
				<tbody>
					<tr>
						<td>
							<input type="checkbox" name="required" >&nbsp;Required field
						</td>
					</tr>
					<tr>
						<td>
							Type<br>
							<select id="leadsquared-tag" name="name">
								<?php 
								$textbox = lsq_search($decode_json, 'RenderTypeTextValue', 'Textbox');
								if($textbox) { $data_type = array(); foreach($textbox as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
									if(!empty($leadsquared_fied_type)) {
										asort($leadsquared_fied_type);
										foreach($leadsquared_fied_type as $field_key => $field_values) {
											if($field_key == 'ProspectID'){
												print '<option  value="'.$field_key.'">'.$field_values.'</option>'; 
											}
											else
											{
												print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
											}
											
										}
									}
									?>
							</select>
						</td>
						<td></td>
					</tr>
				</tbody>
			</table>
			<table>
			<tbody>
				<tr>
					<td>
						<code>id</code> (optional)<br>
						<input type="text" name="id" class="idvalue oneline option">
					</td>
					<td>
						<code>class</code> (optional)<br>
						<input type="text" name="class" class="classvalue oneline option">
					</td>
				</tr>
				<tr>
					<td>
						<code>size</code> (optional)<br>
						<input type="number" name="size" class="numeric oneline option" min="1">
					</td>
					<td>
						<code>maxlength</code> (optional)<br>
						<input type="number" name="maxlength" class="numeric oneline option" min="1">
					</td>
				</tr>
				<tr>
					<td>
						Placeholder text (optional)<br><input type="text" name="values" class="oneline">
					</td>
					<td>
						<br><input type="checkbox" name="placeholder" class="option">&nbsp;Use placeholder text?</td>
				</tr>
			</tbody></table>

			<div class="tg-tag">
				Copy this code and paste it into the form to the left.<br>
				<input id="leadsquared-tag-type" type="text" name="text" class="tag" readonly="readonly" onfocus="this.select()">
			</div>
			<div class="tg-mail-tag">
				And, put this code into the Mail fields below.<br>
				<input type="text" class="mail-tag" readonly="readonly" onfocus="this.select()">
			</div>
		</form>
	</div>
	<div id="wpcf7-tg-pane-leadsquared-textarea" class="hidden">
<form action="">
<table>
<tr><td><input type="checkbox" name="required" />&nbsp;<?php echo esc_html( __( 'Required field?', 'leadsquared' ) ); ?></td></tr>
<tr><td>Type<br>
						<select id="leadsquared-tag" name="name">
							<?php 
							$textarea = lsq_search($decode_json, 'RenderTypeTextValue', 'TextArea');
							if($textarea) { $data_type = array(); foreach($textarea as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td><td></td></tr>
</table>

<table>
<tr>
<td><code>id</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="id" class="idvalue oneline option" /></td>

<td><code>class</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="class" class="classvalue oneline option" /></td>
</tr>

<tr>
<td><code>cols</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="cols" class="numeric oneline option" min="1" /></td>

<td><code>rows</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="rows" class="numeric oneline option" min="1" /></td>
</tr>

<tr>
<td><code>maxlength</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="maxlength" class="numeric oneline option" min="1" /></td>
</tr>

<tr>
<td><?php echo esc_html( __( 'Default value', 'leadsquared' ) ); ?> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br /><input type="text" name="values" class="oneline" /></td>

<td>
<br /><input type="checkbox" name="placeholder" class="option" />&nbsp;<?php echo esc_html( __( 'Use this text as placeholder?', 'leadsquared' ) ); ?>
</td>
</tr>
</table>

<div class="tg-tag"><?php echo esc_html( __( "Copy this code and paste it into the form left.", 'leadsquared' ) ); ?><br /><input type="text" name="textarea" class="tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>

<div class="tg-mail-tag"><?php echo esc_html( __( "And, put this code into the Mail fields below.", 'leadsquared' ) ); ?><br /><input type="text" class="mail-tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>
</form>
</div>
<div id="wpcf7-tg-pane-leadsquared-number" class="hidden">
<form action="">
<table>
<tr><td><input type="checkbox" name="required" />&nbsp;<?php echo esc_html( __( 'Required field?', 'leadsquared' ) ); ?></td></tr>
<tr><td>Type<br>
						<select id="leadsquared-tag" name="name">
							<?php 
							$number = lsq_search($decode_json, 'DataType', 'Number');
							if($number) { $data_type = array(); foreach($number as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td><td></td></tr>
</table>

<table>
<tr>
<td><code>id</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="id" class="idvalue oneline option" /></td>

<td><code>class</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="class" class="classvalue oneline option" /></td>
</tr>

<tr>
<td><code>cols</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="cols" class="numeric oneline option" min="1" /></td>

<td><code>rows</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="rows" class="numeric oneline option" min="1" /></td>
</tr>

<tr>
<td><code>step</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="step" class="numeric oneline option" min="1" /></td>
</tr>

<tr>
<td><?php echo esc_html( __( 'Default value', 'leadsquared' ) ); ?> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br /><input type="text" name="values" class="oneline" /></td>

<td>
<br /><input type="checkbox" name="placeholder" class="option" />&nbsp;<?php echo esc_html( __( 'Use this text as placeholder?', 'leadsquared' ) ); ?>
</td>
</tr>
</table>

<div class="tg-tag"><?php echo esc_html( __( "Copy this code and paste it into the form left.", 'leadsquared' ) ); ?><br /><input type="text" name="number" class="tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>

<div class="tg-mail-tag"><?php echo esc_html( __( "And, put this code into the Mail fields below.", 'leadsquared' ) ); ?><br /><input type="text" class="mail-tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>
</form>
</div>
<div id="wpcf7-tg-pane-leadsquared-number-tel" class="hidden">
<form action="">
<table>
<tr><td><input type="checkbox" name="required" />&nbsp;<?php echo esc_html( __( 'Required field?', 'leadsquared' ) ); ?></td></tr>
<tr><td>Type<br>
						<select id="leadsquared-tag" name="name">
							<?php
							$phone = lsq_search($decode_json, 'DataType', 'Phone');
							if($phone) { $data_type = array(); foreach($phone as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td><td></td></tr>
</table>

<table>
<tr>
<td><code>id</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="id" class="idvalue oneline option" /></td>

<td><code>class</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="class" class="classvalue oneline option" /></td>
</tr>

<tr>
<td><code>cols</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="cols" class="numeric oneline option" min="1" /></td>

<td><code>rows</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="rows" class="numeric oneline option" min="1" /></td>
</tr>

<tr>
<td><?php echo esc_html( __( 'Default value', 'leadsquared' ) ); ?> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br /><input type="text" name="values" class="oneline" /></td>

<td>
<br /><input type="checkbox" name="placeholder" class="option" />&nbsp;<?php echo esc_html( __( 'Use this text as placeholder?', 'leadsquared' ) ); ?>
</td>
</tr>
</table>

<div class="tg-tag"><?php echo esc_html( __( "Copy this code and paste it into the form left.", 'leadsquared' ) ); ?><br /><input type="text" name="tel" class="tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>

<div class="tg-mail-tag"><?php echo esc_html( __( "And, put this code into the Mail fields below.", 'leadsquared' ) ); ?><br /><input type="text" class="mail-tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>
</form>
</div>
<div id="wpcf7-tg-pane-leadsquared-email" class="hidden">
<form action="">
<table>
<tr><td><input type="checkbox" name="required" />&nbsp;<?php echo esc_html( __( 'Required field?', 'leadsquared' ) ); ?></td></tr>
<tr><td>Type<br>
						<select id="leadsquared-tag" name="name">
							<?php 
							$email = lsq_search($decode_json, 'DataType', 'Email');
							if($email) { $data_type = array(); foreach($email as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td><td></td></tr>
</table>

<table>
<tr>
<td><code>id</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="id" class="idvalue oneline option" /></td>

<td><code>class</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="class" class="classvalue oneline option" /></td>
</tr>

<tr>
<td><code>cols</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="cols" class="numeric oneline option" min="1" /></td>

<td><code>rows</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="rows" class="numeric oneline option" min="1" /></td>
</tr>
<tr>
<td colspan="2"><?php echo esc_html( __( 'Akismet', 'leadsquared' ) ); ?> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />

<input type="checkbox" name="akismet:author_email" class="option" />&nbsp;<?php echo esc_html( __( "This field requires author's email address", 'leadsquared' ) ); ?>

</td>
</tr>
<tr>
<td><?php echo esc_html( __( 'Default value', 'leadsquared' ) ); ?> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br /><input type="text" name="values" class="oneline" /></td>

<td>
<br /><input type="checkbox" name="placeholder" class="option" />&nbsp;<?php echo esc_html( __( 'Use this text as placeholder?', 'leadsquared' ) ); ?>
</td>
</tr>
</table>

<div class="tg-tag"><?php echo esc_html( __( "Copy this code and paste it into the form left.", 'leadsquared' ) ); ?><br /><input type="text" name="email" class="tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>

<div class="tg-mail-tag"><?php echo esc_html( __( "And, put this code into the Mail fields below.", 'leadsquared' ) ); ?><br /><input type="text" class="mail-tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>
</form>
</div>
<div id="wpcf7-tg-pane-leadsquared-url" class="hidden">
<form action="">
<table>
<tr><td><input type="checkbox" name="required" />&nbsp;<?php echo esc_html( __( 'Required field?', 'leadsquared' ) ); ?></td></tr>
<tr><td>Type<br>
						<select id="leadsquared-tag" name="name">
							<?php 
							$website = lsq_search($decode_json, 'DataType', 'Website');
							if($website) { $data_type = array(); foreach($website as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td><td></td></tr>
</table>

<table>
<tr>
<td><code>id</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="id" class="idvalue oneline option" /></td>

<td><code>class</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="class" class="classvalue oneline option" /></td>
</tr>

<tr>
<td><code>cols</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="cols" class="numeric oneline option" min="1" /></td>

<td><code>rows</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="number" name="rows" class="numeric oneline option" min="1" /></td>
</tr>
<tr>
<td colspan="2"><?php echo esc_html( __( 'Akismet', 'leadsquared' ) ); ?> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />

<input type="checkbox" name="akismet:author_url" class="option" />&nbsp;<?php echo esc_html( __( "This field requires author's URL", 'leadsquared' ) ); ?>

</td>
</tr>
<tr>
<td><?php echo esc_html( __( 'Default value', 'leadsquared' ) ); ?> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br /><input type="text" name="values" class="oneline" /></td>

<td>
<br /><input type="checkbox" name="placeholder" class="option" />&nbsp;<?php echo esc_html( __( 'Use this text as placeholder?', 'leadsquared' ) ); ?>
</td>
</tr>
</table>

<div class="tg-tag"><?php echo esc_html( __( "Copy this code and paste it into the form left.", 'leadsquared' ) ); ?><br /><input type="text" name="url" class="tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>

<div class="tg-mail-tag"><?php echo esc_html( __( "And, put this code into the Mail fields below.", 'leadsquared' ) ); ?><br /><input type="text" class="mail-tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>
</form>
</div>
<div id="wpcf7-tg-pane-leadsquared-date" class="hidden">
<form action="">
<table>
<tr><td><input type="checkbox" name="required" />&nbsp;<?php echo esc_html( __( 'Required field?', 'leadsquared' ) ); ?></td></tr>
<tr><td>Type<br>
						<select id="leadsquared-tag" name="name">
							<?php 
							$date = lsq_search($decode_json, 'DataType', 'Date');
							if($date) { $data_type = array(); foreach($date as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td><td></td></tr>
</table>

<table>
<tr>
<td><code>id</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="id" class="idvalue oneline option" /></td>

<td><code>class</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="class" class="classvalue oneline option" /></td>
</tr>


<tr>
<td><code>min</code> (<?php echo esc_html( __( 'optional', 'contact-form-7' ) ); ?>)<br />
<input type="date" name="min" class="date oneline option" /></td>

<td><code>max</code> (<?php echo esc_html( __( 'optional', 'contact-form-7' ) ); ?>)<br />
<input type="date" name="max" class="date oneline option" /></td>
</tr>

<tr>
<td><code>step</code> (<?php echo esc_html( __( 'optional', 'contact-form-7' ) ); ?>)<br />
<input type="number" name="step" class="numeric oneline option" min="1" /></td>
</tr>
<tr>
<td><?php echo esc_html( __( 'Default value', 'leadsquared' ) ); ?> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br /><input type="text" name="values" class="oneline" /></td>

<td>
<br /><input type="checkbox" name="placeholder" class="option" />&nbsp;<?php echo esc_html( __( 'Use this text as placeholder?', 'leadsquared' ) ); ?>
</td>
</tr>
</table>

<div class="tg-tag"><?php echo esc_html( __( "Copy this code and paste it into the form left.", 'leadsquared' ) ); ?><br /><input type="text" name="date" class="tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>

<div class="tg-mail-tag"><?php echo esc_html( __( "And, put this code into the Mail fields below.", 'leadsquared' ) ); ?><br /><input type="text" class="mail-tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>
</form>
</div>
<div id="wpcf7-tg-pane-leadsquared-select" class="hidden">
<form action="">
<table>
<tr><td><input type="checkbox" name="required" />&nbsp;<?php echo esc_html( __( 'Required field?', 'leadsquared' ) ); ?></td></tr>
<tr><td>Type<br>
						<select id="leadsquared-tag" name="name">
							<?php 
							$select = lsq_search($decode_json, 'DataType', 'Select');
							if($select) { $data_type = array(); foreach($select as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td><td></td></tr>
</table>

<table>
<tr>
<td><code>id</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="id" class="idvalue oneline option" /></td>

<td><code>class</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="class" class="classvalue oneline option" /></td>
</tr>

<tr>
<td><?php echo esc_html( __( 'Choices', 'leadsquared' ) ); ?><br />
<textarea name="values"></textarea><br />
<span style="font-size: smaller"><?php echo esc_html( __( "* One choice per line.", 'leadsquared' ) ); ?></span>
</td>

<td>
<br /><input type="checkbox" name="multiple" class="option" />&nbsp;<?php echo esc_html( __( 'Allow multiple selections?', 'leadsquared' ) ); ?>
<br /><input type="checkbox" name="include_blank" class="option" />&nbsp;<?php echo esc_html( __( 'Insert a blank item as the first option?', 'leadsquared' ) ); ?>
</td>
</tr>
</table>

<div class="tg-tag"><?php echo esc_html( __( "Copy this code and paste it into the form left.", 'leadsquared' ) ); ?><br /><input type="text" name="select" class="tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>

<div class="tg-mail-tag"><?php echo esc_html( __( "And, put this code into the Mail fields below.", 'leadsquared' ) ); ?><br /><input type="text" class="mail-tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>
</form>
</div>
<div id="wpcf7-tg-pane-leadsquared-ys" class="hidden">
<form action="">
<table>
<tr><td><input type="checkbox" name="required" />&nbsp;<?php echo esc_html( __( 'Required field?', 'leadsquared' ) ); ?></td></tr>
<tr><td>Type<br>

						<select id="leadsquared-tag" name="name">
							<?php 
							$boolean = lsq_search($decode_json, 'DataType', 'Boolean');
							if($boolean) { $data_type = array(); foreach($boolean as $key => $value) {$data_type[$value['SchemaName']] = $value['DisplayName'];}$leadsquared_fied_type = array_unique($data_type);}
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										print '<option  value="leadsquared-'.$field_key.'">'.$field_values.'</option>'; 
									}
								}
								?>
						</select></td><td></td></tr>
</table>

<table>
<tr>
<td><code>id</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="id" class="idvalue oneline option" /></td>

<td><code>class</code> (<?php echo esc_html( __( 'optional', 'leadsquared' ) ); ?>)<br />
<input type="text" name="class" class="classvalue oneline option" /></td>
</tr>

<tr>
<td colspan="2">
<br /><input type="checkbox" name="default:on" class="option" />&nbsp;<?php echo esc_html( __( "Make this checkbox checked by default?", 'leadsquared' ) ); ?>
<br /><input type="checkbox" name="invert" class="option" />&nbsp;<?php echo esc_html( __( "Make this checkbox work inversely?", 'leadsquared' ) ); ?>
<br /><span style="font-size: smaller;"><?php echo esc_html( __( "* That means visitor who accepts the term unchecks it.", 'leadsquared' ) ); ?></span>
</td>
</tr>
</table>

<div class="tg-tag"><?php echo esc_html( __( "Copy this code and paste it into the form left.", 'leadsquared' ) ); ?><br /><input type="text" name="acceptance" class="tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>

<div class="tg-mail-tag"><?php echo esc_html( __( "And, put this code into the Mail fields below.", 'leadsquared' ) ); ?><br /><input type="text" class="mail-tag wp-ui-text-highlight code" readonly="readonly" onfocus="this.select()" /></div>
</form>
</div>