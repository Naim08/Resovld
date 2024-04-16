import os

from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language


class DocumentLoader:

    @staticmethod
    def detect_language_from_extension(extension: str) -> Language:
        """Returns the corresponding Language enum based on the file extension."""
        mapping = {
            ".cpp": Language.CPP,
            ".go": Language.GO,
            ".java": Language.JAVA,
            ".js": Language.JS,
            ".php": Language.PHP,
            ".proto": Language.PROTO,
            ".py": Language.PYTHON,
            ".rst": Language.RST,
            ".rb": Language.RUBY,
            ".rs": Language.RUST,
            ".scala": Language.SCALA,
            ".swift": Language.SWIFT,
            ".md": Language.MARKDOWN,
            ".tex": Language.LATEX,
            ".html": Language.HTML,
            ".sol": Language.SOL,
            # ... add other extensions if needed
        }

        return mapping.get(extension, None)

    def load_and_split_files(self, directory_path: str, repo: str):
        all_texts = []  # A list to collect all split texts

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                print(f"Currently processing: {file}")  # Add this
                extension = os.path.splitext(file)[1]
                language = self.detect_language_from_extension(extension)
                if language is None:
                    print("skipping: " + file)
                    continue

                print("Processing: " + file)
                loader = GenericLoader.from_filesystem(
                    root,
                    glob=f"**/*{extension}",
                    suffixes=[extension],
                    parser=LanguageParser(language=language, parser_threshold=500),
                )

                documents = loader.load()
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=language, chunk_size=2000, chunk_overlap=200
                )
                texts = splitter.split_documents(documents)  # list of documents
                for doc in texts:
                    rpath = root[len(directory_path) + 1:] + "/" + file
                    doc.metadata["rpath"] = rpath
                    doc.metadata["repo"] = repo
                    all_texts.append(doc)

        return all_texts  # Return the list of all split texts
