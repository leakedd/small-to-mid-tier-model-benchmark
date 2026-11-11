# Question banks

All items used in the benchmark, with their expected answers. Items were written
in French during the original study and are reproduced here in English. Correct
options are marked **bold**.

## Battery A — cyber (7)

**A1. GCM nonce reuse.** A service encrypts with AES-256-GCM and a 96-bit random
nonce. After 2^32 messages the nonce generator is replaced by a counter that
restarts whenever the service reboots. What is the main consequence of reusing a
key/nonce pair?
A. Only confidentiality is lost, integrity checking stays reliable
B. Only integrity checking is lost
C. **Confidentiality and integrity are both lost, and message forgery becomes possible**
D. None, GCM is safe because the nonce is 96 bits

**A2. JWT algorithm confusion.** An API verifies JWT with an RSA public key. The
server reads the algorithm from the alg header and explicitly rejects alg=none.
An attacker knows the public key. Which attack forges a valid token?
A. Set alg to none and strip the signature
B. **Set alg to HS256 and sign the token with the public key used as an HMAC secret**
C. Replay another user's token
D. Modify the kid field to point at a local file

**A3. SSRF filter bypass.** A SSRF filter rejects any URL whose text contains
169.254.169.254. The server is a standard Linux host with DNS resolution. Which
bypasses still work?
A. None, the filter covers every case
B. Only changing the port
C. **The decimal integer form of the address, the IPv6-mapped form, and a DNS name resolving to it**
D. Only HTTPS instead of HTTP

**A4. CSP nonce and strict-dynamic.** A page sends
Content-Security-Policy: script-src nonce-abc123 strict-dynamic. An attacker
injects a script with a remote src and no nonce attribute. What does the browser do?
A. It runs the script because strict-dynamic allows remote scripts
B. **It blocks the script because it does not carry the expected nonce**
C. It runs the script if the domain uses HTTPS
D. It ignores the CSP because it contains strict-dynamic

**A5. SUID and PATH.** A root binary carries the SUID bit and calls system with
"ls" without an absolute path, inheriting PATH. How do you get a root shell?
A. **Place a fake ls executable in a directory present in PATH**
B. Modify /etc/ld.so.preload
C. Exploit a race in /tmp
D. Run sudo -l

**A6. Golden ticket.** Which secret is needed to forge a valid Kerberos golden ticket?
A. The NTLM hash of a domain administrator
B. **The KRBTGT account key**
C. The domain controller password
D. The target service ticket

**A7. TLS 1.3 and RSA.** Why did TLS 1.3 remove RSA key exchange?
A. Because it is slower than ECDHE
B. **Because it provides no forward secrecy**
C. Because it is vulnerable to POODLE
D. Because it does not support certificates

## Battery A — systems (7)

**A8. MESI.** Two cores share a cache line, initially Modified on the first. The
second core reads the line. What happens?
A. **The first writes the line back to memory and both become Shared**
B. The first stays Modified and the second receives a copy with no transition
C. The first becomes Invalid without a writeback
D. Both become Exclusive

**A9. TCP TIME_WAIT.** What is the purpose of TIME_WAIT?
A. To guarantee delivery of application data
B. **To absorb late duplicate segments and allow retransmission of the final ACK**
C. To speed up reopening the same port
D. To prevent network congestion

**A10. SSA phi.** What is a phi function for in SSA form?
A. **Choosing a value by predecessor when several control paths merge**
B. Implementing a loop
C. Allocating registers
D. Inlining a function

**A11. Release semantics.** What does a store with release semantics guarantee in
a weak memory model?
A. That earlier loads are not reordered after it
B. **That earlier loads and stores are not reordered after it**
C. That following operations block
D. That it is sequentially consistent

**A12. B+tree.** Why is a B+tree preferred to a binary tree for a disk index with
range scans?
A. Because it is always smaller
B. **Because leaves are linked and the height is low, so a range scan touches few disk blocks**
C. Because it avoids writes
D. Because it is simpler to implement

**A13. TLB shootdown.** A process shares a page with another process then unmaps
it. What must the kernel do on other cores?
A. Nothing, hardware invalidates alone
B. **Invalidate the matching TLB entries on the other cores**
C. Copy the page before unmapping
D. Flush the whole L3 cache

**A14. Priority inversion.** Which mechanism prevents priority inversion?
A. Round robin
B. **Priority inheritance**
C. Time sharing
D. A negative nice value

## Battery A — code (4)

**A15. Path containment.** Write **path_is_within(base, target)** returning True
only if the absolute path target is strictly inside base after normalisation.
It must reject traversal and the prefix trap (base /srv/data must not accept
/srv/data2). Tests include /srv/data/../etc (False) and /srv/data/a/../../data/b
(True).

**A16. JWT verifier.** Write **jwt_verify(token, secret)** for HS256 without
external libraries: base64url without padding, HMAC-SHA256 compared in constant
time, reject any alg other than HS256 and any invalid signature, return the
payload dict or None.

**A17. Binary search on a predicate.** Write **binary_search_first_true(pred, lo, hi)**
returning the smallest index in [lo, hi] where the monotone predicate holds, or -1.

**A18. Cycle detection.** Write **has_cycle(n, edges)** for a directed graph given
as (u, v) tuples.

## Battery B — calculation (7)

**B1. TCP goodput.** A lossless connection has MSS 1460 bytes, RTT 40 ms and a
receive window of 65535 bytes which is the limiting factor. Maximum goodput in
Mbit/s, one decimal? **13.1**

**B2. LRU hits.** A 3-entry LRU cache sees blocks 1 2 3 4 1 2 5 1 2 3 4 5. How
many hits? **2**

**B3. Page table size.** 48-bit virtual address, 4096-byte pages, four levels of
9 index bits. How many entries in the top-level table? **512**

**B4. Amdahl.** A task is 80 percent parallelisable. Maximum speedup with 16
cores, one decimal? **4.0**

**B5. RSA without padding.** RSA with e=3, modulus n=3233 and ciphertext
c=110592, message smaller than n and no padding. Plaintext m? **48**

**B6. SQL injection in ORDER BY.** Code builds
"SELECT * FROM t WHERE id = %s ORDER BY " + column with cursor.execute(q, (uid,)),
where column comes from a ?sort= parameter validated against a whitelist. What
flaw remains if validation is removed? **SQL injection is possible in ORDER BY,
because an identifier cannot be a bound parameter**

**B7. TOCTOU.** Code does if not os.path.exists(p): shutil.copy(src, p). Main
security problem? **A race window between test and write, allowing a link to be
followed or a file overwritten**

## Battery B — code (4)

**B8. Segment tree.** **range_sum_ops(n, arr, ops)** applying ('add', i, v) and
('sum', l, r), returning the list of sums, logarithmic per operation.

**B9. Rabin-Karp.** **count_occurrences(text, pat)** counting overlapping
occurrences with a rolling hash.

**B10. Dijkstra.** **shortest_paths(n, edges, src)** returning distances to every
vertex, -1 when unreachable.

**B11. Matrix chain.** **matrix_chain(dims)** returning the minimum number of
scalar multiplications.

## Battery C — crypto and algorithms (4)

**C1. ChaCha20.** **chacha20_block(key, counter, nonce)** producing the 64-byte
keystream block. The first 16 bytes for key 00..1f, counter 1, nonce
000000090000004a00000000 must equal 10f1e7e4d13b5915500fdd1fa32071c4 (RFC 8439).

**C2. HKDF.** **hkdf_sha256(ikm, salt, info, length)** implementing RFC 5869
extract then expand. For IKM 0x0b*22, salt 000102030405060708090a0b0c, info
f0f1f2f3f4f5f6f7f8f9 and length 42, the OKM must equal the RFC 5869 test vector.

**C3. Regex engine.** **regex_match(pattern, text)** supporting literals, dot and
Kleene star, full match. Must return True for c*a*b against aab and False for
mis*is*p*. against mississippi.

**C4. Suffix array.** **suffix_array(s)** returning start indices of suffixes in
lexicographic order.

## Battery D — cyber (12)

**D1. ECB.** What do identical plaintext blocks produce under ECB?
**Identical ciphertext blocks**

**D2. Kerberoasting.** What does Kerberoasting consist of? **Requesting a service
ticket for an SPN and cracking its hash offline**

**D3. NTLM relay.** Relaying NTLM is primarily blocked by? **Mandatory SMB signing**

**D4. CAP_NET_RAW.** Which Linux capability allows raw sockets without root?
**CAP_NET_RAW**

**D5. IMDSv2.** AWS instance metadata IMDSv2 requires? **A token obtained with a
PUT request and a header**

**D6. HttpOnly.** A cookie marked HttpOnly prevents? **Reading it from JavaScript
through document.cookie**

**D7. Stack canary.** A stack canary primarily detects? **Overwrite of the saved
return address by a linear buffer overflow**

**D8. ASLR bypass.** Which primitive is needed to reliably bypass ASLR? **A memory
address leak**

**D9. JWT kid injection.** An injectable JWT kid field typically allows?
**Path traversal toward an attacker controlled key file**

**D10. Certificate pinning.** Pinning protects against? **A compromised CA issuing
a rogue certificate**

**D11. Padding oracle.** A padding oracle attack targets? **CBC with PKCS#7 padding**

**D12. Second order SQL injection.** It triggers when? **A stored input is reused
in a later query**

## Battery D — systems (10)

**D13. False sharing.** Two cores modifying distinct variables on the same cache line.

**D14. Fast retransmit.** Triggered by **three duplicate ACKs**.

**D15. Heap build.** Building a binary heap from n elements costs **O(n)**.

**D16. Consistent hashing.** Limits **the number of keys moved when a node is added**.

**D17. Copy on write.** After fork, child memory is **shared for reading until the first write**.

**D18. Two phase commit.** Blocks when **the coordinator fails after the prepare phase**.

**D19. Bloom filter.** Produces **false positives but no false negatives**.

**D20. RAID 5 write hole.** Occurs when **a stripe write is interrupted and parity stays inconsistent**.

**D21. NUMA.** A remote access is **slower than a local access**.

**D22. Spinlock.** Preferred when **the critical section is very short and the core is dedicated**.

## Battery D — numeric (4)

**D23.** 64 GiB address space with 8 KiB pages: entries in the last level page table? **2^23**

**D24.** Segments exchanged to open and normally close a TCP connection? **7**

**D25.** Maximum plaintext length with RSA-2048 and PKCS#1 v1.5? **245 bytes**

**D26.** Standard AES-GCM authentication tag size? **16 bytes**

## Battery D — code (4)

**D27.** **merge_k(lists)** merging sorted lists without sorted or heapq.

**D28.** **n_queens(n)** returning the number of distinct solutions.

**D29.** **edit_distance(a, b)** Levenshtein by dynamic programming.

**D30.** **solve_sudoku(board)** returning the solved 9x9 grid or None.

## Battery E — repair loop (2)

**E1. Broken ChaCha20.** The implementation performs four double rounds instead of
ten. Tests compare the keystream against RFC 8439. The model gets three attempts,
with the failing assertion returned after each failure.

**E2. Broken regex.** The matcher advances greedily over a star without
backtracking, so c*a*b against aab fails. Same three-attempt rule.
