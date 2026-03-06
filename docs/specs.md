# Moodisc Specification (Rule-Based)

## 1) Inputs (User Questions)
ALL questions are quantative for simplicity.

Q1. Battery level (1-7)
Q2. Internal monologue loudness (1-7)
Q3. Buffer before hitting limit (1-7)
Q4. Color representing current state (red, blue, yellow, purple, green)

## 2) Color -> Numeric Mapping

- Red: 1.0 (High stress / emergency)
- Blue: 2.0 (Low energy / melancholy)
- Purple: 3.0 (Calm / introspective)
- Yellow: 5.5 (High energy / alert)
- Green: 7.0 (Balanced / growth)

## 3) Mood Percentage Calculation
Let 'color_value' be the numeric value from the mapping above.

mood_raw = Q1 + Q2 + Q3 + color_value
mood_PCT = mood_raw * 3.57

### Rounding value (v1)
- Store mood_pct as a float rounded to 2 decimal places.
- Display mood_pct as a whole number using round(mood_pct).

## 4) Mood Buckets (Exact Boundary Rules)

- Bucket A: 0 <= mood_pct < 20
- Bucket B: 20 <= mood_pct < 40
- Bucket C: 40 <= mood_pct < 60
- Bucket D: 60 <= mood_pct < 85
- Bucket E: 85 <= mood_pct <= 100

## 5) Genre Buckets

Bucket A (0-19): slowcore, drone, dark-ambient, neoclassical-darkwave, chamber-folk
Bucket B (20-39): neo-psychedelia, chamber-pop, dream-pop, shoegaze, conscious hip-hop
Bucket C (40-59): baroque-pop, trap-soul, orchestral, contemporary-r&b, alternative-r&b
Bucket D (60-84): trap, electronic, industrial metal, nu jazz, experimental hip-hop
Bucket E (85-100): pop rap, digicore, hyperpop, future-bass, desconstructed club, bubblegum bass, jazz-rap, dance-pop

## 6) Recommendation Output
- The system returns N = 4 songs per session.

## 7) Feedback (Thumbs Up / Down) - v1
The recommendated selection can be rated:

- Thumbs Up: positive feedback
- Thumbs Down: negative feedback

The system stores feedback for the user and will bias future recommendations:
- More of genres associated with thumbs-up songs
- Less of genres associated with thumbs-down songs

(Exact weighting is defined in Week 1 implementation as a simple genre preference score.)