// Edit your code blow:
#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Constants.h"
#include "llvm/Support/CFG.h"
#include "klee/Internal/ADT/KTest.h"
#include "klee/Interpreter.h"
#include "Memory.h"
#include "Executor.h"
//#include "llvm/Analysis/LoopInfo.h"
//#include "llvm/PassManager.h"
#include "PathSkipHelper.h"
//#include "CommonUtils.h"
#include <vector>
#include <algorithm>

using namespace llvm;
using namespace klee;
using namespace pskipper;

//class KleeHandler;

// Weikun 10/4/2016
PathSkipHelper::PathSkipHelper(Executor *executor, ExecutionState &trueState, ExecutionState &falseState):executor_(executor), trueState_(trueState), falseState_(falseState) {
    trueInLoop_ = false;
    falseInLoop_ = false;
    onlyState_ = 2;
}

PathSkipHelper::PathSkipHelper(Executor *executor, ExecutionState &state, bool singleState):executor_(executor), trueState_(state), falseState_(state) {
	trueInLoop_ = false;
	falseInLoop_ = false;
	
    if (singleState) {
    	onlyState_ = 1;
    } else {
    	onlyState_ = 0;
	}
}

PathSkipHelper::~PathSkipHelper() {}

bool PathSkipHelper::checkStateSkippable() {
	if (onlyState_ == 0) {
	    return isStateInLoop(falseState_, falseInLoop_, false);
	} else if (onlyState_ == 1) {
    	return isStateInLoop(trueState_, trueInLoop_, true);
    } else {
    	return isStateInLoop(trueState_, trueInLoop_, true) || isStateInLoop(falseState_, falseInLoop_, false);
    }
}

bool PathSkipHelper::isStateInLoop(ExecutionState &state, bool &inLoop, bool dir) {
	if (executor_->copyHistMap.count(&state)) {
    	executor_->copyHistMap[&state]++;
//   if (executor_->copyHistMap.size()< executor_->copyHistLimit) return false;
  	}
  	inLoop = false;
  //Get current instruction and Basicblock
  BasicBlock* currBB = state.prevPC->inst->getParent();
  if (!executor_->exitHeadMap.count(currBB)) return false;
  //Run loop pass to see whether correspoding bb e nds to loop
  //PassManager pass_manager;
  //PassRegistry &Registry = *llvm::PassRegistry::getPassRegistry();
  //initializeAnalysis(Registry);
  
  //Function* currFn = currBB->getParent();
  //Module* currModule = currBB->getParent()->getParent();
  //pass_manager.add(new llvm::LoopInfo());
  //LoopIdentify* lIden = new LoopIdentify(currFn, currBB, dir);
  //pass_manager.add(lIden);
  //pass_manager.run(*currModule);
  //errs()<<"Here\n";
  //BasicBlock* currHeader = lIden->header;
  //Since LoopPass failed to detect some inner loops, dk why
  //We wil continue using KMP style matching on the constriantPath 
  //to identify smallest loop over there.
  unsigned repeatNum = 1;
  int loopLen = 1;
 //  if (currHeader == NULL) {
 //    return false;
 // int sz = state.constraintPath.size();
 // std::vector<int> prefix(sz, 0);
 // std::vector<int> vecPaths = state.constraintPath;
 // std::reverse(vecPaths.begin(), vecPaths.end());
 // //KMP style prefix calculation
 // int index = 0;  
 // for (int i = 1; i < sz;) {
 //   if (vecPaths[i] == vecPaths[index]) {
 //     prefix[i] = ++index;
 //     i++;
 //   }
 //   else if (index != 0){
 //     index = prefix[index-1];
 //   }
 //   else {
 //     prefix[i] = 0;
 //     i++;
 //   }
 // }
 // int maxLen = 1;
 // //errs()<<"Path: \n";
 // //for (auto& path: vecPaths) {
 // //  errs()<<path<<" ";
 // //}
 // //errs()<<"Prefix:\n";
 // //errs()<<"\n";
 // //for (auto& pre: prefix) {
 // //  errs()<<pre<<" ";
 // //}
 // //errs()<<"\n";
 // std::vector<int> vecLen(sz,1);
 // for (int i = 1; i < sz; i++) {
 //   if (prefix[i] - prefix[i-1] == 1 && prefix[i-1] != 0) {
 //     vecLen[i] = vecLen[i-1]+1;
 //     loopLen = vecLen[i]>maxLen? i-vecLen[i]+1 : loopLen;  
 //     maxLen = std::max(maxLen, vecLen[i]);
 //   }
 //   else {
 //     vecLen[i] = 1; 
 //   }
 // }
 // if (loopLen <= 0) return false;
 // if (loopLen < maxLen) {
 //   repeatNum += maxLen/loopLen;
 // }  
 // std::vector<int> vecLoop (state.constraintPath.end()-loopLen, state.constraintPath.end());
 // if (repeatNum > 6){ 
 //   if (!checkLoop(state, currBB, vecLoop))
 //     return false;
 //   state.repeatNum = repeatNum;
 //   state.currLoopLen = loopLen;
 //   state.vecLoop = vecLoop;
 //   inLoop = true;
 //   return true;
 // }
//  }
//End of KMP
  //else {
    BasicBlock* currHeader = executor_->exitHeadMap[currBB];
    int szBBPath = state.BBPath.size();
    int i = 0;
    for (i = szBBPath-1; i >= 0; i--) {
      if (state.BBPath[i] == currHeader) break;
    }
    assert(state.BBPath.size()==state.constraintPath.size() && "BBPath and constraint Path are of diff size");
    loopLen = szBBPath - i;
  
    std::vector<int> vecLoop (state.constraintPath.begin()+i, state.constraintPath.end());
//    int idxCompEnd = i-1;
//    while (idxCompEnd - loopLen + 1 >= 0) {
//      std::vector<int> compareLoop(state.constraintPath.begin()+idxCompEnd-loopLen+1, state.constraintPath.begin()+idxCompEnd+1);
//      if (std::equal(compareLoop.begin(), compareLoop.end(), vecLoop.begin())) {
//        idxCompEnd -= loopLen;
//        repeatNum++;
//      }
//      else 
//        break;
//    }
//    if (repeatNum > 3) {
      state.repeatNum = repeatNum;
      state.currLoopLen = loopLen;
      state.vecLoop = vecLoop;
      inLoop = true;
      return true;
//    }
  //}
  
  return false;
  //find head of the loop
  //get length of the loop
  //checking constraint path pattern and get loopLen and repeated num
}

void PathSkipHelper::skipState() {
  if (trueInLoop_) skipStateInternal(trueState_);
  if (falseInLoop_) skipStateInternal(falseState_); 
}

void PathSkipHelper::skipStateInternal(ExecutionState &state) {
  state.copyCount = 0;
  state.step = 1;
  state.currForkIdx = 0;
  executor_->flagCopying = true;
  executor_->loopState = &state;
  executor_->backUpState = new ExecutionState(state);
  executor_->copyStateStackStat(*(executor_->backUpState), state);
//  executor_->copyHistMap[&state]++;
  //if (executor_->copyHistMap.size()>=executor_->copyHistLimit)
    //executor_->removeLargestQueryHist();
}

void PathSkipHelper::getKInstFromClause(ExecutionState& state, ref<Expr> clause, KInstruction*& ki) {
  StackFrame &sf = state.stack.back();
  KFunction* kf = sf.kf;
  unsigned regNum = kf->numRegisters;
  unsigned index = 0;
  for (index = 0; index < regNum; index++) {
    unsigned clauseHash = clause->hash();
    if (!sf.locals[index].value.isNull() && sf.locals[index].value->hash() == clauseHash) {
      break;
    }
  }
  for (unsigned kInstIdx = 0; kInstIdx < kf->numInstructions; kInstIdx++) {
    KInstruction* currKInst = kf->instructions[kInstIdx];
    if (currKInst->dest == index) {
      ki = currKInst;
      break;
    }
  }
  //assert(ki!=NULL && "NULL KI in  getKInstFromClause\n");
}

bool PathSkipHelper::checkLoop(ExecutionState& state, BasicBlock* curr, std::vector<int> vecLoop) {
  //count # non-2,3 BB
  int cnt = 0;
  for (auto& elem: vecLoop) {
    if (elem == 0 || elem == 1) cnt++;
  }
  if (cnt == 0) return false;
  else return true;
//  BasicBlock* dest = curr;
//  if (cnt != 0) {
//    int sz = state.constraints.constraints.size();
//    ref<Expr> cond = state.constraints.constraints[sz-cnt];
//    KInstruction* kinst = NULL;
//    getKInstFromClause(state, cond, kinst);
//    if (kinst == NULL) return false;
//    dest = kinst->inst->getParent();
//  }
//  return dfsLoop(curr, dest, vecLoop.size(), 0);
}

bool PathSkipHelper::dfsLoop(BasicBlock* curr, BasicBlock* dest, int sz, int depth) {
  if (depth > sz) return false;
  int cnt = 0;
  for (succ_iterator iter =  succ_begin(curr); iter != succ_end(curr); ++iter) {
    cnt++;
  }
  if (cnt > 1)  depth++;
  for (succ_iterator iter =  succ_begin(curr); iter != succ_end(curr); ++iter) {
    BasicBlock* succ = *iter;
    if (succ == dest) return true;
    if (dfsLoop(succ, dest, sz, depth)) return true;
  }
  return false;
}
