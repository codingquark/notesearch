#!/usr/bin/env python3
"""
Test script to verify GPU setup for the semantic notes search system.
"""

import torch
import faiss
import time
import numpy as np
from sentence_transformers import SentenceTransformer


def test_gpu_setup():
    """Test GPU availability and basic functionality."""
    print("=== GPU Setup Test ===\n")
    
    # Test PyTorch CUDA
    print("1. PyTorch CUDA Test:")
    if torch.cuda.is_available():
        print(f"   ✓ CUDA available: {torch.cuda.get_device_name()}")
        print(f"   ✓ CUDA version: {torch.version.cuda}")
        print(f"   ✓ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        
        # Test basic GPU operations
        device = torch.device('cuda')
        x = torch.randn(1000, 1000).to(device)
        y = torch.randn(1000, 1000).to(device)
        
        start_time = time.time()
        z = torch.mm(x, y)
        torch.cuda.synchronize()
        gpu_time = time.time() - start_time
        
        print(f"   ✓ GPU matrix multiplication: {gpu_time:.4f}s")
    else:
        print("   ✗ CUDA not available")
        return False
    
    # Test FAISS (CPU version with GPU embeddings)
    print("\n2. FAISS Test:")
    try:
        # Test CPU index creation
        dimension = 384  # Typical embedding dimension
        index = faiss.IndexFlatIP(dimension)
        print("   ✓ FAISS CPU index created")
        
        # Test with sample data
        vectors = np.random.rand(1000, dimension).astype(np.float32)
        faiss.normalize_L2(vectors)
        
        start_time = time.time()
        index.add(vectors)
        cpu_time = time.time() - start_time
        print(f"   ✓ CPU index add: {cpu_time:.4f}s")
        
    except Exception as e:
        print(f"   ✗ FAISS error: {e}")
        return False
    
    # Test Sentence Transformers GPU
    print("\n3. Sentence Transformers GPU Test:")
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        model = model.to('cuda')
        print("   ✓ Model moved to GPU")
        
        # Test embedding generation
        texts = ["This is a test sentence.", "Another test sentence for GPU acceleration."]
        
        start_time = time.time()
        embeddings = model.encode(texts, device='cuda')
        torch.cuda.synchronize()
        gpu_time = time.time() - start_time
        
        print(f"   ✓ GPU embedding generation: {gpu_time:.4f}s")
        print(f"   ✓ Embedding shape: {embeddings.shape}")
        
    except Exception as e:
        print(f"   ✗ Sentence Transformers GPU error: {e}")
        return False
    
    print("\n=== All GPU Tests Passed! ===")
    print("Your RTX 2080 Ti is ready for semantic search acceleration.")
    print("Note: Using PyTorch GPU acceleration for embeddings with CPU FAISS for search.")
    return True


def performance_comparison():
    """Compare CPU vs GPU performance for embedding generation."""
    print("\n=== Performance Comparison ===")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = [f"This is test sentence number {i} for performance testing." for i in range(100)]
    
    # CPU test
    print("Testing CPU performance...")
    start_time = time.time()
    cpu_embeddings = model.encode(texts, device='cpu')
    cpu_time = time.time() - start_time
    
    # GPU test
    print("Testing GPU performance...")
    model = model.to('cuda')
    start_time = time.time()
    gpu_embeddings = model.encode(texts, device='cuda')
    torch.cuda.synchronize()
    gpu_time = time.time() - start_time
    
    print(f"\nResults:")
    print(f"  CPU time: {cpu_time:.4f}s")
    print(f"  GPU time: {gpu_time:.4f}s")
    print(f"  Speedup: {cpu_time/gpu_time:.1f}x")
    
    # Verify results are similar
    if isinstance(cpu_embeddings, torch.Tensor):
        cpu_embeddings = cpu_embeddings.cpu().numpy()
    if isinstance(gpu_embeddings, torch.Tensor):
        gpu_embeddings = gpu_embeddings.cpu().numpy()
    diff = np.abs(cpu_embeddings - gpu_embeddings).max()
    print(f"  Max difference: {diff:.6f} (should be < 1e-5)")


if __name__ == "__main__":
    if test_gpu_setup():
        performance_comparison()
    else:
        print("\nGPU setup failed. Please check your CUDA installation.") 