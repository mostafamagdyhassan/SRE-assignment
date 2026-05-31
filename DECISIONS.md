# DECISIONS.md


# Technical Decisions

## 1. Event-Driven Architecture (S3 → SQS)

**Alternatives considered:** S3 polling  
**Decision:** Use SQS event notifications  
**Why:** Reduces unnecessary polling, lowers latency, and aligns with production-grade AWS patterns.  
**With more time:** Add DLQ and redrive policies.

---

## 2. Single Container (Scanner + ClamAV)

**Alternatives considered:** Separate ClamAV service container  
**Decision:** Single container  
**Why:** Reduces network complexity, avoids TCP socket exposure, simplifies deployment.  
**With more time:** Separate ClamAV for independent scaling.

---

## 3. clamd vs clamscan

**Alternatives considered:** clamscan CLI  
**Decision:** clamd (daemon mode)  
**Why:** Avoids signature reload per scan; significantly reduces latency.  
**With more time:** Tune memory usage and thread count.

---

## 4. Idempotency Check via Object Tags

**Alternatives considered:** External state store (Redis/DB)  
**Decision:** Use S3 object tags  
**Why:** Keeps system stateless and simplifies architecture.  
**With more time:** Add checksum-based deduplication.

---

## 5. ThreadPool Concurrency

**Alternatives considered:** AsyncIO or multiprocessing  
**Decision:** ThreadPoolExecutor  
**Why:** Simpler implementation; ClamAV scan is external process, so GIL is not limiting.  
**With more time:** Add dynamic worker scaling based on queue depth.

---

## 6. At-Least-Once Semantics

**Alternatives considered:** Exactly-once processing  
**Decision:** Accept at-least-once delivery from SQS  
**Why:** Simpler and reliable; idempotency makes duplicates safe.  
**With more time:** Add DLQ monitoring.

---

## 7. Prometheus Metrics

**Alternatives considered:** No metrics  
**Decision:** Expose metrics endpoint  
**Why:** Enables SLO measurement and operational visibility.  
**With more time:** Add structured logging and alerting rules.
