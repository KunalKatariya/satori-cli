"""Translation module using Meta NLLB (No Language Left Behind) models."""

import logging
from typing import Optional

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logger = logging.getLogger(__name__)


class Translator:
    """Offline translation using Meta NLLB models.

    Supports Japanese <-> English <-> Hindi translation with automatic language detection.
    Uses Meta's NLLB-200 model for high-quality translation.
    """

    # NLLB language codes
    LANG_CODES = {
        "ja": "jpn_Jpan",  # Japanese
        "en": "eng_Latn",  # English
        "hi": "hin_Deva",  # Hindi
    }

    def __init__(self, target_language: str = "en", model_size: str = "600M") -> None:
        """Initialize translator.

        Args:
            target_language: Target language code ('en', 'ja', or 'hi')
            model_size: Model size - '600M' (faster, 1.2GB) or '1.3B' (better quality, 2.7GB)
        """
        self.target_language = target_language
        self.model_size = model_size
        self.model: Optional[AutoModelForSeq2SeqLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model_loaded = False

        # Detect best available device (GPU if available, otherwise CPU)
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info("Using CUDA GPU for translation")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
            logger.info("Using Apple Metal GPU for translation")
        else:
            self.device = torch.device("cpu")
            logger.info("Using CPU for translation (GPU not available)")

        # Choose model based on size
        if model_size == "1.3B":
            self.model_name = "facebook/nllb-200-1.3B"
        else:
            self.model_name = "facebook/nllb-200-distilled-600M"

        logger.info(
            f"Translator initialized: target={target_language}, model={self.model_name}, device={self.device}"
        )

    def _load_model(self) -> None:
        """Load translation model (lazy loading on first use)."""
        if self.model_loaded:
            return

        logger.info(
            f"Loading NLLB translation model: {self.model_name} (this may take a minute)..."
        )

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

        # Move model to GPU if available
        self.model = self.model.to(self.device)
        self.model_loaded = True

        logger.info(f"NLLB model loaded successfully on {self.device}")

    def _detect_language(self, text: str) -> str:
        """Detect if text is Japanese, Hindi, or English.

        Args:
            text: Input text

        Returns:
            Language code ('ja', 'hi', or 'en')
        """
        # Check for Japanese characters (Hiragana, Katakana, Kanji)
        japanese_chars = sum(1 for char in text if "\u3040" <= char <= "\u9fff")
        # Check for Hindi characters (Devanagari script)
        hindi_chars = sum(1 for char in text if "\u0900" <= char <= "\u097f")
        total_chars = len(text)

        if total_chars == 0:
            return "en"

        # If more than 20% Japanese characters, consider it Japanese
        if japanese_chars / total_chars > 0.2:
            return "ja"
        # If more than 20% Hindi characters, consider it Hindi
        if hindi_chars / total_chars > 0.2:
            return "hi"
        return "en"

    def translate(self, text: str) -> str:
        """Translate text to target language.

        Automatically detects source language and translates to target.

        Args:
            text: Text to translate

        Returns:
            Translated text
        """
        if not text.strip():
            return ""

        try:
            # Load model on first use
            self._load_model()

            # Detect source language
            source_lang = self._detect_language(text)
            print(
                f"\n[TRANSLATION] Detected source: {source_lang} | Text: '{text[:50]}...'",
                flush=True,
            )
            logger.info(
                f"Detected source language: {source_lang} for text: '{text[:50]}...'"
            )

            # Skip if already in target language
            if source_lang == self.target_language:
                print(
                    f"[TRANSLATION] Skipping - already in target language ({self.target_language})",
                    flush=True,
                )
                logger.warning(
                    f"Text already in target language ({self.target_language}), skipping translation"
                )
                return text

            # Get NLLB language codes
            source_code = self.LANG_CODES.get(source_lang)
            target_code = self.LANG_CODES.get(self.target_language)

            if not source_code or not target_code:
                print(
                    f"[TRANSLATION] Error: Unsupported language pair {source_lang}->{self.target_language}",
                    flush=True,
                )
                logger.warning(
                    f"Unsupported language pair: {source_lang}->{self.target_language}"
                )
                return text

            print(
                f"[TRANSLATION] Translating {source_code} -> {target_code}...",
                flush=True,
            )
            logger.info(f"Translating {source_code} -> {target_code}")

            # Tokenize with source language
            self.tokenizer.src_lang = source_code
            inputs = self.tokenizer(
                text, return_tensors="pt", padding=True, truncation=True, max_length=512
            )

            # Move input tensors to the same device as the model
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate translation with target language
            # NLLB uses convert_tokens_to_ids to get the language token ID
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(target_code)
            translated = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=200,  # Reduced from 512 for faster inference
                num_beams=2,  # Reduced from 5 for lower latency (greedy-like speed)
                early_stopping=True,  # Stop when all beams finish
                length_penalty=0.8,  # Slightly prefer shorter outputs for speed
            )
            translated_text = self.tokenizer.decode(
                translated[0], skip_special_tokens=True
            )

            print(f"[TRANSLATION] Result: '{translated_text[:100]}...'", flush=True)
            logger.info(
                f"Translation result: '{text[:50]}...' -> '{translated_text[:50]}...'"
            )

            return translated_text

        except Exception as e:
            print(f"[TRANSLATION] ERROR: {e}", flush=True)
            logger.error(f"Translation error: {e}")
            import traceback

            traceback.print_exc()
            logger.error(traceback.format_exc())
            return text  # Return original on error
