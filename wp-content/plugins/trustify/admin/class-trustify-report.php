<?php

if ( ! class_exists( 'WP_List_Table' ) ) {
    require_once ABSPATH . 'wp-admin/includes/class-wp-list-table.php';
}

class Trustify_Clicks_Report extends WP_List_Table {

    /**
     * Total number of found users for the current query
     *
     * @since 3.1.0
     * @var int
     */
    private $total_count = 0;

    public function __construct() {
        parent::__construct( array(
            'singular' => 'report',
            'plural'   => 'reports',
            'ajax'     => false,
            'screen'   => 'trustify-click-report',
        ) );
    }

    public function get_columns() {
        return array(
            'report_id'     => __( 'ID', 'trustify' ),
            'product_name'  => __( 'Product Name', 'trustify' ),
            'count'         => __( 'Clicks Count', 'trustify' ),
        );
    }

    /**
     * Prepare the items for the table to process
     *
     * @return Void
     */
    public function prepare_items() {
        $columns  = $this->get_columns();
        $hidden   = $this->get_hidden_columns();
        $sortable = $this->get_sortable_columns();

        $perPage     = $this->get_items_per_page( 'reports_per_page', 10 );
        $currentPage = $this->get_pagenum();

        $data = $this->table_data( ( $currentPage - 1 ) * $perPage, $perPage );
        $this->_column_headers = array( $columns, $hidden, $sortable );
        $this->items = $data;

        $this->set_pagination_args( array(
            'total_items' => $this->total_count,
            'per_page'    => $perPage
        ) );
    }

    /**
     * Define which columns are hidden
     *
     * @return Array
     */
    public function get_hidden_columns() {
        return array();
    }

    /**
     * Define the sortable columns
     *
     * @return Array
     */
    public function get_sortable_columns() {
        return array('count'=>array('count',true));
    }



    /**
     * Get the table data
     *
     * @return Array
     */
    private function table_data( $lower = 0, $uper = 10 ) {
        global $wpdb;
        $data    = array();

        $query = "SELECT * FROM {$wpdb->base_prefix}trustify_report";

        $from = ( isset( $_GET['DateFrom'] ) && $_GET['DateFrom'] ) ? $_GET['DateFrom'] : date('Y-m-d');
        $to = ( isset( $_GET['DateTo'] ) && $_GET['DateTo'] ) ? $_GET['DateTo'] : date('Y-m-d');
        $to = date('Y-m-d', strtotime($to . ' +1 day'));
        
        if( isset($_GET['DateFrom']) ){
            $query .= " WHERE date BETWEEN '{$from}' AND '{$to}'";
        }

        $query .= " GROUP BY product_id";

        if(isset($_GET['orderby']) && $_GET['orderby'] == 'count'){
            $order = $_GET['order'];

            $query .= " ORDER BY COUNT(product_id) {$order}";
        }

        $query .= " LIMIT {$lower},{$uper}";
      
        $reports = $wpdb->get_results($query);

        //Get Total Item Count
        $tquery = "SELECT COUNT( DISTINCT product_id ) FROM {$wpdb->base_prefix}trustify_report";
        if(isset( $_GET['DateFrom'])){
            $tquery .= " WHERE (date BETWEEN '{$from}' AND '{$to}')";
        }

        $this->total_count = (int) $wpdb->get_var( $tquery );

        if ( ! empty( $reports ) && is_array( $reports ) ) {
            foreach ( $reports as $key => $report ) {
                
                $cquery = "SELECT COUNT(*) FROM {$wpdb->base_prefix}trustify_report WHERE product_id={$report->product_id}";
                
                if(isset( $_GET['DateFrom'])){
                    $cquery .= " AND (date BETWEEN '{$from}' AND '{$to}')";
                }
                $count = (int) $wpdb->get_var( $cquery );

                $data[] = array(
                    'report_id' => $report->report_id,
                    'product_name' => '<a href="'.get_the_permalink($report->product_id).'" target="_blank">'.get_the_title($report->product_id).'</a>',
                    'count'           => $count
                );
            }
        }
        return $data;
    }

    /**
     * Define what data to show on each column of the table
     *
     * @param  Array $item        Data
     * @param  String $column_name - Current column name
     *
     * @return Mixed
     */
    public function column_default( $item, $column_name ) {
        switch ( $column_name ) {
            case 'report_id':
            case 'product_name':
            case 'count':
                return $item[$column_name];
            default:
                return print_r( $item, true );
        }
    }

}
