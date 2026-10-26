export default function Methodology() {
  const steps = [
    {
      num: '01',
      title: 'Problem Statement & Challenge Rules',
      desc: 'Business Entity Resolution resolves noisy records from independent sources (Source 2 and Source 3) to reference entities in Source 1. Official evaluation prioritizes precision via the F0.5 metric, heavily penalizing false-positive match hallucinations.',
    },
    {
      num: '02',
      title: 'Memory-Safe Large Dataset Processing',
      desc: 'With 26.4 million rows across 7 TSV files, in-memory blind loading crashes processes. Our pipeline uses chunked streaming, precomputed inspection metadata, and a SQLite candidate index to ensure instantaneous queries and sub-100MB execution footprints.',
    },
    {
      num: '03',
      title: 'Open-Set Country Robustness',
      desc: 'Training contains primarily US and India, but the held-out test set contains France (259k records) and unseen geographies. Country is engineered as a general comparison feature rather than a hard-coded whitelist filter.',
    },
    {
      num: '04',
      title: 'Unicode NFKC & Suffix Normalization',
      desc: 'Normalizes multilingual Unicode strings, trims whitespaces, maps corporate suffixes (inc, llc, ltd, corp, gmbh, pvt, sa, plc), and standardizes postal addresses (street -> st, road -> rd, avenue -> ave, suite -> ste).',
    },
    {
      num: '05',
      title: 'High-Recall Multi-Block Blocking',
      desc: 'Avoids O(N×M) comparison explosions using 5 complementary blocking keys: (country + 3-char prefix), (exact normalized name), (country + significant token), (open-set token), and (country + address prefix).',
    },
    {
      num: '06',
      title: '14-Feature Vector Engineering',
      desc: 'Extracts Levenshtein ratios, RapidFuzz partial ratio, token sort ratio, token set ratio, token Jaccards for names and addresses, length difference proportions, and address missingness indicators.',
    },
    {
      num: '07',
      title: 'Hard-Negative Training Pair Generation',
      desc: 'Pairs true matches from train_ground_truth.tsv with hard negatives mined from the same blocking buckets and same country having high phonetic or lexical overlap but different underlying entities.',
    },
    {
      num: '08',
      title: 'HistGradientBoosting Tree Ensemble',
      desc: 'Trained using scikit-learn HistGradientBoostingClassifier with balanced class weighting, leaf regularization, and permutation feature importance analysis. Local execution compliant and < 8B parameters.',
    },
    {
      num: '09',
      title: 'Data-Leakage Free Validation Split',
      desc: 'Validation split is strictly grouped by Source 1 entity ID, ensuring that all candidate pairs for any given reference business exist exclusively in either train or validation, preventing overoptimistic leakage.',
    },
    {
      num: '10',
      title: 'F0.5 Metric Optimization & Threshold Tuning',
      desc: 'Sweeps probability cutoffs from 0.30 to 0.95 in 0.05 steps to maximize F0.5 = (1.25 × P × R) / (0.25 × P + R). An optimal threshold of 0.90 achieves 99.7% Precision and 0.9952 F0.5.',
    },
    {
      num: '11',
      title: 'Candidate Subset Rule Enforcement',
      desc: 'Conceptually and practically guarantees that all matched entity IDs in matching_results.tsv are a strict mathematical subset of candidate_pairs.tsv. Zero, single, and multiple matches are fully supported.',
    },
    {
      num: '12',
      title: '12-Rule Official Validator',
      desc: 'Automates verification of column formatting, tab delimiters, missing rows, duplicate IDs, invalid format identifiers, and subset containment prior to final competition submission.',
    },
  ]

  return (
    <div className="methodology-page">
      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>System Architecture & Technical Methodology</h3>
            <p className="panel-subtext">Comprehensive breakdown of our Amazon ML Challenge solution</p>
          </div>
          <span className="badge badge-match">End-to-End Complete</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', marginTop: '16px' }}>
          {steps.map((s) => (
            <div
              key={s.num}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#818cf8' }}>{s.num}</span>
              <h4 style={{ color: '#fff', fontSize: '1rem' }}>{s.title}</h4>
              <p style={{ fontSize: '0.84rem', color: '#cbd5e1', lineHeight: '1.5' }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
