Steps to use:

Run

```bash
python3 generate_big_json_csv.py
```

It will generate 2 big files
 - "data.csv" ~0.4G
 - "data.json" ~1.2G

Now, run

```bash
python3 read_csv.py
```

See the output

```txt
Value1
Elapsed time: 0.0494 seconds
Memory usage: 11680.00 MB
```

Now, run

```bash
python3 read_json.py
```

See the output

```txt
Your system has run out of application memory.
```

Both scripts are printing the second column from the record number 1000

Also you can change the variables from the script to generate different size of files:

```python
num_columns = 500
num_records = 1000000
```

Notice that the I/O disk usage could degrade the performance if the disk is used by other process

Notice that swaping RAM memory to disk could degrade the performance too much

Results:

```python
num_columns = 500
num_records = 100000
```

```bash
python3 read_csv.py
# Value1
# Elapsed time: 0.0492 seconds
# Memory usage: 11,632.00 MB

python3 read_json.py
# Value1
# Elapsed time: 6.4161 seconds
# Memory usage: 4,593,648.00 MB
```


```python
num_columns = 500
num_records = 1000000
```


```bash
python3 read_csv.py
# Value1
# Elapsed time: 0.053 seconds
# Memory usage: 11,408.00 MB

python3 read_json.py
# My laptop stuck and I had to restart with the power button pressed for 5 seconds
```

Better using docker to avoid stucking my laptop and using lower values

```python
num_columns = 500
num_records = 100000
# 419M data.csv
# 1.2G data.json
```


```bash
docker run -it --rm -v /Users/moylop260/odoo/json_vs_csv:/root/json_vs_csv -m 2g --memory-swap=6g quay.io/vauxoo/nocustomers:odoo-17.0-latest /root/json_vs_csv/read_json.py
# Elapsed time: 18.4197 seconds
# RAM Memory usage: 2,045 MB
# Swap Memory Information: 3,289,864 MB
```

```bash
docker run -it --rm -v /Users/moylop260/odoo/json_vs_csv:/root/json_vs_csv -m 2g --memory-swap=6g quay.io/vauxoo/nocustomers:odoo-17.0-latest /root/json_vs_csv/read_csv.py
# Elapsed time: 0.0524 seconds
# RAM Memory usage: 24 MB
# Swap Memory Information: 2,056 MB
```

<img width="1511" alt="Screenshot 2024-04-12 at 2 30 00 p m  copy" src="https://github.com/vauxoo-dev/gist-vauxoo/assets/6644187/6507cc09-829d-4087-980a-42e76589eb7a">


Notice the use of the swap reading the whole file could be slower for system loaded

Also, notice the I/O rate could affects here
