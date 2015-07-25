// matrix/sparse-matrix.cc

// Copyright 2015     Johns Hopkins University (author: Daniel Povey)

// See ../../COPYING for clarification regarding multiple authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
// WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
// MERCHANTABLITY OR NON-INFRINGEMENT.
// See the Apache 2 License for the specific language governing permissions and
// limitations under the License.

#include "matrix/sparse-matrix.h"
#include "matrix/kaldi-matrix.h"
#include <algorithm>

namespace kaldi {

template <typename Real>
void SparseVector<Real>::CopyToVec(VectorBase<Real> *vec) const {
  KALDI_ASSERT(vec->Dim() == this->dim_);
  vec->SetZero();
  Real *other_data = vec->Data();
  typename std::vector<std::pair<MatrixIndexT, Real> >::const_iterator
      iter = pairs_.begin(), end = pairs_.end();
  for (; iter != end; ++iter)
    other_data[iter->first] = iter->second;
}
  

template <typename Real>
void SparseVector<Real>::AddToVec(Real alpha,
                                   VectorBase<Real> *vec) const {
  KALDI_ASSERT(vec->Dim() == dim_);
  Real *other_data = vec->Data();
  typename std::vector<std::pair<MatrixIndexT, Real> >::const_iterator
      iter = pairs_.begin(), end = pairs_.end();
  if (alpha == 1.0) {  // treat alpha==1.0 case specially.
    for (; iter != end; ++iter)
      other_data[iter->first] += iter->second;
  } else {
    for (; iter != end; ++iter)
      other_data[iter->first] += alpha * iter->second;
  }
}

template <typename Real>
SparseVector<Real>& SparseVector<Real>::operator = (
    const SparseVector<Real> &other) {
  dim_ = other.dim_;
  pairs_ = other.pairs_;
  return *this;
}

template <typename Real>
void SparseVector<Real>::Swap(SparseVector<Real> *other) {
  pairs_.swap(other->pairs_);
  std::swap(dim_, other->dim_);
}

template <typename Real>
void SparseVector<Real>::Write(std::ostream &os, bool binary) const {
  if (binary) {
    WriteToken(os, binary, "SV");
    WriteBasicType(os, binary, dim_);
    MatrixIndexT num_elems = pairs_.size();
    WriteBasicType(os, binary, num_elems);
    typename std::vector<std::pair<MatrixIndexT, Real> >::const_iterator
        iter = pairs_.begin(), end = pairs_.end();
    for (; iter != end; ++iter) {
      WriteBasicType(os, binary, iter->first);
      WriteBasicType(os, binary, iter->second);
    }
  } else {
    // In text-mode, use a human-friendly, script-friendly format;
    // format is "dim=5 [ dim=5 0 0.2 3 0.9 ] "
    os << "dim=" << dim_ << " ";
    typename std::vector<std::pair<MatrixIndexT, Real> >::const_iterator
        iter = pairs_.begin(), end = pairs_.end();
    for (; iter != end; ++iter)
      os << iter->first << ' ' << iter->second << ' ';
    os << "] ";
  }
}


template <typename Real>
void SparseVector<Real>::Read(std::istream &is, bool binary) {
  if (binary) {
    ExpectToken(is, binary, "SV");
    ReadBasicType(is, binary, &dim_);
    KALDI_ASSERT(dim_ >= 0);
    int32 num_elems;
    ReadBasicType(is, binary, &num_elems);
    KALDI_ASSERT(num_elems >= 0 && num_elems <= dim_);
    pairs_.resize(num_elems);
    typename std::vector<std::pair<MatrixIndexT, Real> >::iterator
        iter = pairs_.begin(), end = pairs_.end();
    for (; iter != end; ++iter) {
      ReadBasicType(is, binary, &(iter->first));
      ReadBasicType(is, binary, &(iter->second));
    }
  } else {
    // In text-mode, format is "dim=5 [ 0 0.2 3 0.9 ]
    std::string str;
    is >> str;
    if (str.substr(0, 4) != "dim=")
      KALDI_ERR << "Reading sparse vector, expected 'dim=xxx', got " << str;
    std::string dim_str = str.substr(4, std::string::npos);
    std::istringstream dim_istr(dim_str);
    int32 dim = -1;
    dim_istr >> dim;
    if (dim < 0 || dim_istr.fail()) {
      KALDI_ERR << "Reading sparse vector, expected 'dim=[int]', got " << str;
    }
    dim_ = dim;
    is >> std::ws;
    is >> str;
    if (str != "[")
      KALDI_ERR << "Reading sparse vector, expected '[', got " << str;
    pairs_.clear();
    while (1) {
      is >> std::ws;
      if (is.peek() == ']') {
        is.get();
        break;
      }
      MatrixIndexT i; BaseFloat p;
      is >> i >> p;
      if (is.fail())
        KALDI_ERR << "Error reading sparse vector, expecting numbers.";
      KALDI_ASSERT(i >= 0 && i < dim && (pairs_.empty() || i > pairs_.back().first));
      pairs_.push_back(std::pair<MatrixIndexT, BaseFloat>(i, p));
    }
  }
}


namespace sparse_vector_utils {
template <typename Real>
struct CompareFirst {
  inline bool operator () (const std::pair<MatrixIndexT, Real> &p1,
                           const std::pair<MatrixIndexT, Real> &p2) const {
    return p1.first < p2.first;
  }
};
}

template <typename Real>
SparseVector<Real>::SparseVector(MatrixIndexT dim,
                                 const std::vector<std::pair<MatrixIndexT, Real> > &pairs):
    dim_(dim),
    pairs_(pairs) {
  std::sort(pairs_.begin(), pairs_.end(),
            sparse_vector_utils::CompareFirst<Real>());
  typename std::vector<std::pair<MatrixIndexT,Real> >::iterator
      out = pairs_.begin(), in = out,  end = pairs_.end();
  // special case: while there is nothing to be changed, skip over
  // initial input (avoids unnecessary copying).
  while (in + 1 < end && in[0].first != in[1].first && in[0].second != 0.0) {
    in++;
    out++;
  }
  while (in < end) {
    // We reach this point only at the first element of
    // each stretch of identical .first elements.
    *out = *in;
    ++in;
    while (in < end && in->first == out->first) {
      out->second += in->second; // this is the merge operation.
      ++in;
    }
    if (out->second != Real(0.0)) // Don't keep zero elements.
      out++;
  }
  pairs_.erase(out, end);
  if (!pairs_.empty()) {
    // range check.
    KALDI_ASSERT(pairs_.front().first >= 0 && pairs_.back().first < dim_);
  }
}

template <typename Real>
void SparseVector<Real>::SetRandn(BaseFloat zero_prob) {
  pairs_.clear();
  KALDI_ASSERT(zero_prob >= 0 && zero_prob <= 1.0);
  for (MatrixIndexT i = 0; i < dim_; i++)
    if (WithProb(1.0 - zero_prob))
      pairs_.push_back(std::pair<MatrixIndexT,Real>(i, RandGauss()));
}

template <typename Real>
void SparseVector<Real>::Resize(MatrixIndexT dim, MatrixResizeType resize_type) {
  if (resize_type != kCopyData || dim == 0)
    pairs_.clear();
  KALDI_ASSERT(dim >= 0);
  if (dim < dim_ && resize_type == kCopyData)
    while (!pairs_.empty() && pairs_.back().first >= dim)
      pairs_.pop_back();
  dim_ = dim;
}

template <typename Real>
MatrixIndexT SparseMatrix<Real>::NumRows() const {
  return rows_.size();
}

template <typename Real>
MatrixIndexT SparseMatrix<Real>::NumCols() const {
  if (rows_.empty())
    return 0.0;
  else
    return rows_[0].Dim();
}

template <typename Real>
void SparseMatrix<Real>::CopyToMat(MatrixBase<Real> *other,
                                   MatrixTransposeType trans) const {
  if (trans == kNoTrans) {
    MatrixIndexT num_rows = rows_.size();
    KALDI_ASSERT(other->NumRows() == num_rows);
    for (MatrixIndexT i = 0; i < num_rows; i++) {
      SubVector<Real> vec(*other, i);
      rows_[i].CopyToVec(&vec);
    }
  } else {
    Real *other_col_data = other->Data();
    MatrixIndexT other_stride = other->Stride(),
        num_rows = NumRows(), num_cols = NumCols();
    KALDI_ASSERT(num_rows == other->NumCols() && num_cols == other->NumRows());
    other->SetZero();
    for (MatrixIndexT row = 0; row < num_rows; row++, other_col_data++) {
      const SparseVector<Real> &svec = rows_[row];
      MatrixIndexT num_elems = svec.NumElements();
      const std::pair<MatrixIndexT, Real> *sdata = svec.Data();
      for (MatrixIndexT e = 0; e < num_elems; e++)
        other_col_data[sdata[e].first * other_stride] = sdata[e].second;
    }
  }
}

template <typename Real>
void SparseMatrix<Real>::Write(std::ostream &os, bool binary) const {
  if (binary) {
    // Note: we can use the same marker for float and double SparseMatrix, because
    // internally we use WriteBasicType and ReadBasicType to read the floats and
    // doubles, and this will automatically take care of type conversion.
    WriteToken(os, binary, "SM");
    int32 num_rows = rows_.size();
    WriteBasicType(os, binary, num_rows);
    for (int32 row = 0; row < num_rows; row++)
      rows_[row].Write(os, binary);
  } else {
    // The format is "rows=10 dim=20 [ 1 0.4  9 1.2 ] dim=20 [ 3 1.7 19 0.6 ] ....
    // not 100% efficient, but easy to work with, and we can re-use the read/write code
    /// from SparseVector.
    int32 num_rows = rows_.size();
    os << "rows=" << num_rows << " ";
    for (int32 row = 0; row < num_rows; row++)
      rows_[row].Write(os, binary);
    os << "\n";  // Might make it a little more readable.
  }
}

template <typename Real>
void SparseMatrix<Real>::Read(std::istream &is, bool binary) {
  if (binary) {
    ExpectToken(is, binary, "SM");
    int32 num_rows;
    ReadBasicType(is, binary, &num_rows);
    KALDI_ASSERT(num_rows >= 0 && num_rows < 10000000);
    rows_.resize(num_rows);
    for (int32 row = 0; row < num_rows; row++)
      rows_[row].Read(is, binary);
  } else {
    std::string str;
    is >> str;
    if (str.substr(0, 5) != "rows=")
      KALDI_ERR << "Reading sparse matrix, expected 'rows=xxx', got " << str;
    std::string rows_str = str.substr(5, std::string::npos);
    std::istringstream rows_istr(rows_str);
    int32 num_rows = -1;
    rows_istr >> num_rows;
    if (num_rows < 0 || rows_istr.fail()) {
      KALDI_ERR << "Reading sparse vector, expected 'rows=[int]', got " << str;
    }
    rows_.resize(num_rows);
    for (int32 row = 0; row < num_rows; row++)
      rows_[row].Read(is, binary);
  }
  
}


template <typename Real>
void SparseMatrix<Real>::AddToMat(BaseFloat alpha,
                                  MatrixBase<Real> *other,
                                  MatrixTransposeType trans) const {
  if (trans == kNoTrans) {
    MatrixIndexT num_rows = rows_.size();
    KALDI_ASSERT(other->NumRows() == num_rows);
    for (MatrixIndexT i = 0; i < num_rows; i++) {
      SubVector<Real> vec(*other, i);
      rows_[i].AddToVec(alpha, &vec);
    }
  } else {
    Real *other_col_data = other->Data();
    MatrixIndexT other_stride = other->Stride(),
        num_rows = NumRows(), num_cols = NumCols();
    KALDI_ASSERT(num_rows == other->NumCols() && num_cols == other->NumRows());
    for (MatrixIndexT row = 0; row < num_rows; row++, other_col_data++) {
      const SparseVector<Real> &svec = rows_[row];
      MatrixIndexT num_elems = svec.NumElements();
      const std::pair<MatrixIndexT, Real> *sdata = svec.Data();
      for (MatrixIndexT e = 0; e < num_elems; e++)
        other_col_data[sdata[e].first * other_stride] += alpha * sdata[e].second;
    }
  }
}


template <typename Real>
std::pair<MatrixIndexT, Real>* SparseVector<Real>::Data() {
  if (pairs_.empty()) return NULL;
  else return &(pairs_[0]);
}

template <typename Real>
const std::pair<MatrixIndexT, Real>* SparseVector<Real>::Data() const {
  if (pairs_.empty()) return NULL;
  else return &(pairs_[0]);
}

template <typename Real>
Real VecSvec(const VectorBase<Real> &vec,
             const SparseVector<Real> &svec) {
  KALDI_ASSERT(vec.Dim() == svec.Dim());
  MatrixIndexT n = svec.NumElements();
  const std::pair<MatrixIndexT,Real> *sdata = svec.Data();
  Real *data = vec.Data();
  Real ans = 0.0;
  for (MatrixIndexT i = 0; i < n; i++)
    ans += data[sdata[i].first] * sdata[i].second;
  return ans;
}

template <typename Real>
const SparseVector<Real> &SparseMatrix<Real>::Row(MatrixIndexT r) const {
  KALDI_ASSERT(static_cast<size_t>(r) < rows_.size());
  return rows_[r];
}
    
template <typename Real>
SparseMatrix<Real>& SparseMatrix<Real>::operator = (
    const SparseMatrix<Real> &other) {
  rows_ = other.rows_;
  return *this;
}

template <typename Real>
void SparseMatrix<Real>::Swap(SparseMatrix<Real> *other) {
  rows_.swap(other->rows_);
}

template<typename Real>
SparseMatrix<Real>::SparseMatrix(MatrixIndexT dim,
 const std::vector<std::vector<std::pair<MatrixIndexT, Real> > > &pairs):
    rows_(pairs.size()) {
  MatrixIndexT num_rows = pairs.size();
  for (MatrixIndexT row = 0; row < num_rows; row++) {
    SparseVector<Real> svec(dim, pairs[row]);
    rows_[row].Swap(&svec);
  }
}

template <typename Real>
void SparseMatrix<Real>::SetRandn(BaseFloat zero_prob) {
  MatrixIndexT num_rows = rows_.size();
  for (MatrixIndexT row = 0; row < num_rows; row++)
    rows_[row].SetRandn(zero_prob);
}

template <typename Real>
void SparseMatrix<Real>::Resize(MatrixIndexT num_rows,
                                MatrixIndexT num_cols,
                                MatrixResizeType resize_type) {
  KALDI_ASSERT(num_rows >= 0 && num_cols >= 0);
  if (resize_type == kSetZero || resize_type == kUndefined) {
    rows_.clear();
    Resize(num_rows, num_cols, kCopyData);
  } else {
    // Assume resize_type == kCopyData from here.
    int32 old_num_rows = rows_.size(), old_num_cols = NumCols();
    SparseVector<Real> initializer(num_cols);
    rows_.resize(num_rows, initializer);
    if (num_cols != old_num_cols)
      for (int32 row = 0; row < old_num_rows; row++)
        rows_[row].Resize(num_cols, kCopyData);
  }
}


template<typename Real>
Real TraceMatSmat(const MatrixBase<Real> &A,
                  const SparseMatrix<Real> &B,
                  MatrixTransposeType trans) {
  Real sum = 0.0;
  if (trans == kTrans) {
    MatrixIndexT num_rows = A.NumRows();
    KALDI_ASSERT(B.NumRows() == num_rows);
    for (MatrixIndexT r = 0; r < num_rows; r++)
      sum += VecSvec(A.Row(r), B.Row(r));
  } else {
    const Real *A_col_data = A.Data();
    MatrixIndexT Astride = A.Stride(), Acols = A.NumCols(), Arows = A.NumRows();
    KALDI_ASSERT(Arows == B.NumCols() && Acols == B.NumRows());
    Real sum = 0.0;
    for (MatrixIndexT i = 0; i < Acols; i++,A_col_data++) {
      Real col_sum = 0.0;
      const SparseVector<Real> &svec = B.Row(i);
      MatrixIndexT num_elems = svec.NumElements();
      const std::pair<MatrixIndexT, Real> *sdata = svec.Data();
      for (MatrixIndexT e = 0; e < num_elems; e++)
        col_sum += A_col_data[Astride * sdata[e].first] * sdata[e].second;
      sum += col_sum;
    }
  }
  return sum;
}


void GeneralMatrix::Clear() {
  mat_.Resize(0, 0);
  cmat_.Clear();
  smat_.Resize(0, 0);
}

GeneralMatrix& GeneralMatrix::operator= (const MatrixBase<BaseFloat> &mat) {
  Clear();
  mat_ = mat;
  return *this;
}

GeneralMatrix& GeneralMatrix::operator= (const CompressedMatrix &cmat) {
  Clear();
  cmat_ = cmat;
  return *this;  
}

GeneralMatrix& GeneralMatrix::operator= (const SparseMatrix<BaseFloat> &smat) {
  Clear();
  smat_ = smat;
  return *this;  
}

GeneralMatrix& GeneralMatrix::operator= (const GeneralMatrix &gmat) {
  mat_ = gmat.mat_;
  smat_ = gmat.smat_;
  cmat_ = gmat.cmat_;
  return *this;  
}


GeneralMatrixType GeneralMatrix::Type() const {
  if (smat_.NumRows() != 0)
    return kSparseMatrix;
  else if (cmat_.NumRows() != 0)
    return kCompressedMatrix;
  else
    return kFullMatrix;
}

MatrixIndexT GeneralMatrix::NumRows() const {
  MatrixIndexT r = smat_.NumRows();
  if (r != 0)
    return r;
  r = cmat_.NumRows();
  if (r != 0)
    return r;
  return mat_.NumRows();
}

MatrixIndexT GeneralMatrix::NumCols() const {
  MatrixIndexT r = smat_.NumCols();
  if (r != 0)
    return r;
  r = cmat_.NumCols();
  if (r != 0)
    return r;
  return mat_.NumCols();
}


void GeneralMatrix::Compress() {
  if (mat_.NumRows() != 0) {
    cmat_.CopyFromMat(mat_);
    mat_.Resize(0, 0);
  } 
}

void GeneralMatrix::Uncompress() {
  if (cmat_.NumRows() != 0) {
    cmat_.CopyToMat(&mat_);
    cmat_.Clear();
  }
}

void GeneralMatrix::GetMatrix(Matrix<BaseFloat> *mat) const {
  if (mat_.NumRows() !=0) {
    *mat = mat_;
  } else if (cmat_.NumRows() != 0) {
    mat->Resize(cmat_.NumRows(), cmat_.NumCols(), kUndefined);
    cmat_.CopyToMat(mat);
  } else if (smat_.NumRows() != 0) {
    mat->Resize(smat_.NumRows(), smat_.NumCols(), kUndefined);
    smat_.CopyToMat(mat);
  } else {
    mat->Resize(0, 0);
  }
}

void GeneralMatrix::CopyToMat(MatrixBase<BaseFloat> *mat) const {
  if (mat_.NumRows() !=0) {
    mat->CopyFromMat(mat_);
  } else if (cmat_.NumRows() != 0) {
    cmat_.CopyToMat(mat);
  } else if (smat_.NumRows() != 0) {
    smat_.CopyToMat(mat);
  } else {
    KALDI_ASSERT(mat->NumRows() == 0);
  }
}

void GeneralMatrix::GetSparseMatrix(SparseMatrix<BaseFloat> *smat) const {
  if (Type() != kSparseMatrix)
    KALDI_ERR << "GetSparseMatrix called on GeneralMatrix of wrong type.";
  *smat = smat_;        
}

void GeneralMatrix::GetCompressedMatrix(CompressedMatrix *cmat) const {
  if (Type() != kCompressedMatrix)
    KALDI_ERR << "GetSparseMatrix called on GeneralMatrix of wrong type.";
  *cmat = cmat_;
}

void GeneralMatrix::Write(std::ostream &os, bool binary) const {
  if (smat_.NumRows() != 0) {
    smat_.Write(os, binary);
  } else if (cmat_.NumRows() != 0) {
    cmat_.Write(os, binary);
  } else {
    mat_.Write(os, binary);
  }
}

void GeneralMatrix::Read(std::istream &is, bool binary) {
  Clear();
  if (binary) {
    int peekval = is.peek();
    if (peekval == 'C') {
      // Token CM for compressed matrix
      cmat_.Read(is, binary);
    } else if (peekval == 'S') {
      // Token SM for sparse matrix
      smat_.Read(is, binary);
    } else {
      mat_.Read(is, binary);
    }
  } else {
    // note: in text mode we will only ever read regular
    // or sparse matrices, because the compressed-matrix format just
    // gets written as a regular matrix in text mode.
    is >> std::ws;  // Eat up white space.
    int peekval = is.peek();
    if (peekval == 'r') {  // sparse format starts rows=[int].
      smat_.Read(is, binary);
    } else {
      mat_.Read(is, binary);
    }
  }
}
    
template class SparseVector<float>;
template class SparseVector<double>;
template class SparseMatrix<float>;
template class SparseMatrix<double>;



} // namespace kaldi
