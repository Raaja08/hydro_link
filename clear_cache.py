#!/usr/bin/env python3
"""
Clear all Streamlit caches and force fresh deployment
"""
import streamlit as st

def main():
    st.title("🧹 Cache Cleaner")
    st.write("This page clears all Streamlit caches")
    
    if st.button("Clear All Caches"):
        # Clear all caches
        st.cache_data.clear()
        st.cache_resource.clear()
        
        # Force rerun
        st.rerun()
        
    st.success("✅ All caches cleared!")
    st.write("You can now go back to your main app.")

if __name__ == "__main__":
    main()
