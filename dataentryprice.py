import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def load_data(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.csv':
            # latin1 handles most special characters from older exports
            return pd.read_csv(path, encoding='latin1', dtype=str)
        else:
            return pd.read_excel(path, dtype=str)
    except Exception as e:
        raise ValueError(f"Could not read {os.path.basename(path)}: {e}")

def run_update():
    path_web = entry_web.get()
    path_ev = entry_ev.get()

    if not path_web or not path_ev:
        messagebox.showerror("Error", "Please select both files.")
        return

    try:
        df1 = load_data(path_web)
        df2 = load_data(path_ev)

        # 1. Identify Website columns
        web_sku = next((c for c in df1.columns if c.lower() == 'sku'), None)
        web_desc_col = next((c for c in df1.columns if c.lower() == 'name/short description'), 'Name/Short Description')
        # Target 'Price' on the Website file
        web_price_col = next((c for c in df1.columns if c.lower() == 'price'), 'Price')

        # 2. Identify Everest columns
        ev_code = next((c for c in df2.columns if c.lower() == 'code'), None)
        ev_desc = next((c for c in df2.columns if c.lower() == 'description'), None)
        # Target 'Sell Price' on the Everest file
        ev_price = next((c for c in df2.columns if c.lower() == 'sell price'), None)

        # Validation
        if not web_sku:
            messagebox.showerror("Error", "Could not find 'SKU' in Website file.")
            return
        if not all([ev_code, ev_desc, ev_price]):
            messagebox.showerror("Error", f"Everest file needs 'Code', 'Description', and 'Sell Price'.\nFound columns: {list(df2.columns)}")
            return

        # 3. Prepare Everest Data (SKU, Description, Price)
        df2_prepared = df2[[ev_code, ev_desc, ev_price]].copy()
        df2_prepared.columns = ['sku_join', 'desc_new', 'price_new']
        
        # Clean SKU strings for matching
        df1['sku_join'] = df1[web_sku].astype(str).str.strip().str.upper()
        df2_prepared['sku_join'] = df2_prepared['sku_join'].astype(str).str.strip().str.upper()
        df2_prepared = df2_prepared.drop_duplicates(subset=['sku_join'])

        # 4. Merge Data
        updated_df = pd.merge(df1, df2_prepared, on='sku_join', how='left')

        # 5. Handle Description Update
        if web_desc_col in updated_df.columns:
            updated_df[web_desc_col] = updated_df['desc_new'].combine_first(updated_df[web_desc_col])
        else:
            updated_df[web_desc_col] = updated_df['desc_new']

        # 6. Handle Price Update (Replacing Cost logic)
        if web_price_col in updated_df.columns:
            updated_df[web_price_col] = updated_df['price_new'].combine_first(updated_df[web_price_col])
        else:
            updated_df[web_price_col] = updated_df['price_new']

        # Cleanup internal join columns
        cols_to_drop = ['sku_join', 'desc_new', 'price_new']
        updated_df.drop(columns=[c for c in cols_to_drop if c in updated_df.columns], inplace=True)

        # 7. Save result
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("Excel file", "*.xlsx")],
            initialfile="Updated_Inventory_Prices.csv"
        )
        
        if save_path:
            if save_path.endswith('.xlsx'):
                updated_df.to_excel(save_path, index=False)
            else:
                updated_df.to_csv(save_path, index=False)
            messagebox.showinfo("Success", "Descriptions and Prices linked successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# --- GUI ---
root = tk.Tk()
root.title("Inventory Sync: Description & Price")
root.geometry("500x320")

def browse(entry_box):
    fn = filedialog.askopenfilename(filetypes=[("Sheets", "*.csv *.xlsx *.xls")])
    if fn:
        entry_box.delete(0, tk.END)
        entry_box.insert(0, fn)

tk.Label(root, text="Website File (To be updated)", font=('Arial', 10, 'bold')).pack(pady=(20,0))
entry_web = tk.Entry(root, width=55); entry_web.pack(pady=5)
tk.Button(root, text="Browse Website", command=lambda: browse(entry_web)).pack()

tk.Label(root, text="Everest File (Source of Price/Desc)", font=('Arial', 10, 'bold')).pack(pady=(20,0))
entry_ev = tk.Entry(root, width=55); entry_ev.pack(pady=5)
tk.Button(root, text="Browse Everest", command=lambda: browse(entry_ev)).pack()

tk.Button(root, text="SYNC DESCRIPTION & PRICE", command=run_update, 
          bg="#3498db", fg="white", font=('Arial', 12, 'bold'), height=2).pack(pady=30)

root.mainloop()
