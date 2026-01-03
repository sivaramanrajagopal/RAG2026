# Voice Features Documentation

## Overview

The RAG Web Application now includes two voice features:
1. **Voice Search** - Speech-to-text for entering questions
2. **Voice Readout** - Text-to-speech for reading answers

## Features Implemented

### 1. Voice Search (Speech-to-Text)

**Location**: Next to the question input field

**How it works**:
- Click the "Voice Search" button (🎤 icon)
- Browser requests microphone permission (first time only)
- Speak your question
- Text automatically appears in the input field
- Click "Ask Question" to submit

**Technical Details**:
- Uses Web Speech API (`SpeechRecognition`)
- Supports Chrome, Edge, Safari (webkit prefix)
- Language: English (US)
- Real-time transcription
- Visual feedback: Button turns red and shows "Listening..." while recording

**Error Handling**:
- Microphone permission denied → Clear error message
- No microphone found → Helpful error message
- No speech detected → User-friendly notification
- Browser not supported → Button hidden automatically

### 2. Voice Readout (Text-to-Speech)

**Location**: Above the answer text (Play/Stop buttons)

**How it works**:
- After receiving an answer, click "Play Answer" button (▶️)
- Answer is read aloud using browser's text-to-speech
- Click "Stop" button (⏹️) to stop playback
- Automatically stops when answer finishes

**Technical Details**:
- Uses Web Speech API (`speechSynthesis`)
- Automatically removes citation brackets `[filename]` for cleaner speech
- Language: English (US)
- Rate: Normal (1.0x)
- Visual feedback: Button changes color when playing

**Features**:
- Play/Pause functionality
- Stop button appears while playing
- Auto-stops when answer completes
- Stops if user navigates away from page
- Error handling for unsupported browsers

## Browser Compatibility

### Voice Search (Speech Recognition)
- ✅ Chrome/Edge: Full support
- ✅ Safari: Full support (webkit)
- ❌ Firefox: Not supported (uses different API)

### Voice Readout (Text-to-Speech)
- ✅ Chrome/Edge: Full support
- ✅ Safari: Full support
- ✅ Firefox: Full support
- ✅ Most modern browsers

## User Experience

### Voice Search Flow
1. User clicks "Voice Search" button
2. Browser requests microphone permission (if first time)
3. Button turns red, shows "Listening..."
4. User speaks question
5. Text appears in input field
6. User can edit or submit directly

### Voice Readout Flow
1. Answer is displayed
2. User clicks "Play Answer"
3. Play button hides, Stop button appears
4. Answer is read aloud
5. Stop button changes back to Play when finished
6. User can stop anytime

## Security & Privacy

- **Microphone Access**: Only requested when user clicks voice search
- **No Data Storage**: Voice data is not stored or sent to server
- **Client-Side Only**: All voice processing happens in browser
- **Permission-Based**: Requires explicit user permission

## Accessibility

- **ARIA Labels**: All buttons have proper labels
- **Keyboard Accessible**: All controls work with keyboard
- **Screen Reader Support**: Proper announcements for status changes
- **Visual Feedback**: Clear visual indicators for recording/playing states

## Code Implementation

### Key Functions

1. **`initSpeechAPI()`**: Initializes Web Speech APIs
   - Sets up speech recognition
   - Configures text-to-speech
   - Handles browser compatibility

2. **`speakText(text)`**: Converts text to speech
   - Cleans text (removes citations)
   - Creates utterance
   - Handles play/stop states
   - Error handling

3. **Voice Search Handler**: Manages recording
   - Starts/stops recognition
   - Updates UI states
   - Handles errors

## Usage Tips

1. **For Best Results**:
   - Speak clearly and at normal pace
   - Use quiet environment for voice search
   - Allow microphone permission when prompted

2. **Voice Search**:
   - Works best with clear questions
   - Can edit text after recognition
   - Supports natural language

3. **Voice Readout**:
   - Great for long answers
   - Useful for accessibility
   - Can be stopped anytime

## Future Enhancements

- Multiple language support
- Voice speed control (slower/faster)
- Voice pitch adjustment
- Continuous listening mode
- Voice commands (e.g., "stop", "pause")
- Offline voice recognition (if available)

