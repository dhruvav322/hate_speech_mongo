# Comprehensive Test Cases for Hate Speech Detection

## 🎯 Purpose
Validate the ensemble ML model's ability to detect various forms of hate speech across different categories.

## ✅ Test Categories

### 1. **Benign Content (Should Score LOW)**
- "I love this community, everyone is so helpful!"
- "Great job on the project, keep it up!"
- "Thanks for sharing this information"
- "Have a wonderful day everyone"
- Expected: <10% toxicity, action: none

### 2. **Mild Profanity (Should Score LOW-MEDIUM)**
- "This is so damn frustrating"
- "What the hell is going on?"
- "That's crazy, man"
- Expected: 10-30% toxicity, action: none/monitor

### 3. **Insults (Should Score MEDIUM-HIGH)**
- "You're an idiot"
- "Stop being so stupid"
- "bitch ass"
- "You're pathetic"
- Expected: 30-60% toxicity, action: warn

### 4. **Severe Toxicity (Should Score HIGH)**
- "You're fucking stupid and worthless"
- "Go kill yourself"
- "I hate you, you piece of shit"
- "Nobody wants you here, loser"
- Expected: 60-90% toxicity, action: warn/hide

### 5. **Identity-Based Hate (Should Score VERY HIGH)**
- Slurs targeting race, religion, gender, sexuality
- "All [group] should die"
- Dehumanizing language
- Expected: 80-100% toxicity, action: delete/ban

### 6. **Threats (Should Score VERY HIGH)**
- "I'm going to find you and hurt you"
- "You deserve to die"
- "I'll make you regret this"
- Expected: 70-100% toxicity, action: hide/delete

### 7. **Context-Dependent (Tricky Cases)**
- "You killed it!" (positive in gaming context)
- "That's sick!" (can be positive slang)
- "Bitch please" (meme/casual vs aggressive)
- Expected: Variable based on context

### 8. **Multilingual Testing**
- Test with non-English toxic content (multilingual model should catch)
- Spanish, French, German, etc.
- Expected: Multilingual model detects toxicity

### 9. **Obfuscation Attempts**
- "f*ck you"
- "b!tch"
- "a$$hole"
- Expected: Should still detect with moderate confidence

### 10. **Edge Cases**
- Empty string
- Very long text (>1000 chars)
- Special characters only: "!@#$%^&*()"
- Numbers only: "12345"
- Expected: Graceful handling, low/zero toxicity

## 📊 Expected Ensemble Behavior

The **3-model ensemble** should:
1. **Original Detoxify**: General English toxicity
2. **Multilingual Detoxify**: Cross-language support
3. **Unbiased Detoxify**: Reduce false positives on identity terms

### Scoring Breakdown:
- **0-20%**: Safe content
- **20-40%**: Borderline/monitor
- **40-60%**: Warning level
- **60-80%**: Hide/escalate
- **80-100%**: Severe action (delete/ban)

## 🚀 How to Test

### Via Frontend UI:
1. Go to http://localhost:3000
2. Paste each test case
3. Click "Analyze"
4. Verify scores match expected ranges
5. Check category breakdown (toxic, obscene, insult, threat, etc.)

### Via API (cURL):
```bash
curl -X POST http://localhost:8000/api/v1/moderation/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"YOUR_TEST_TEXT","user_id":"test_user"}'
```

### Bulk Testing:
Use the bulk analysis feature in the UI to test multiple cases at once.

## ✨ Success Criteria

✅ **System is working optimally when:**
- Benign content scores <10%
- Severe toxicity scores >70%
- Confidence levels are >40% for clear cases
- Processing time <200ms per text
- No crashes or errors
- Categories align with content (insult vs threat vs obscene)
- All 3 models load successfully at startup
- Database persists results correctly

## 🔧 Troubleshooting

If results seem off:
1. Check backend logs for model loading
2. Verify all 3 models loaded: "Successfully loaded 3 models for ensemble"
3. Ensure MongoDB is connected
4. Check processing time (should be <200ms)
5. Test with known toxic phrases first
6. Compare single-model vs ensemble results

## 📈 Performance Benchmarks

Optimal system performance:
- **Startup time**: <30 seconds (model loading)
- **Single analysis**: <150ms
- **Batch of 10**: <500ms
- **Accuracy**: >90% on clear cases
- **False positive rate**: <5%
