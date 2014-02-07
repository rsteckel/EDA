import csv, os


infile = open(os.environ['NM_HOME']+'/Data/product_catalog_features.tdf', 'r')
outfile = open(os.environ['NM_HOME']+'/Data/product_features.tsv', 'w')


inreader = csv.reader(infile, delimiter='\t')
outwriter = csv.writer(outfile, delimiter='\t')

header = ['id','cmos_item_code_t','categoryType_name_t','category_name_t','edison_dept_t',
        'edison_subclass_t','flg_is_on_promotion_b','flg_is_on_sale_b','sellable_date_dt','regular_price_f',
        'sale_price_f','silo_name_t','brand_name_t','item_name_t','designer_copy_t','product_desc_t']

outwriter.writerow(header)
outfile.flush()

for row in inreader:
    #if len(row) != len(header)-2:
    #if len(row) != len(header):
    #    print 'Missing fields:', row
    #    continue    

    id = row[0]
    cmos_item_code_t = row[1]
    categoryType_name_t = row[2]
    category_name_t = row[3]
    edison_dept_t = row[4]
    edison_subclass_t = row[5]
    flg_is_on_promotion_b = row[6]
    flg_is_on_sale_b = row[7]
    sellable_date_dt = row[8]
    regular_price_f = row[9]
    sale_price_f = row[10]
    silo_name_t = row[11]
    brand_name_t = row[12]
    item_name_t = row[13]
    designer_copy_t = row[14]
    product_desc_t = row[15]



    outwriter.writerow( [id, cmos_item_code_t, categoryType_name_t, category_name_t, edison_dept_t, 
                         edison_subclass_t, flg_is_on_promotion_b, flg_is_on_sale_b, sellable_date_dt, regular_price_f,
                         sale_price_f, silo_name_t, brand_name_t, item_name_t, designer_copy_t, product_desc_t] )

infile.close()
outfile.flush()
outfile.close()