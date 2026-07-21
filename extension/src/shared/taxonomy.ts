// Stub definitions for taxonomy

export const CATEGORY_IDS: any = {
    AI: 'ai',
    DEVELOPER_TOOLS: 'developer_tools'
};

export function getCategoryById(id: string): any {
    return { id, name: id };
}

export function getAllCategories(): any[] {
    return [];
}

export function getAllInterests(): any[] {
    return [];
}

export type TaxonomyCategory = any;
export type TaxonomyInterest = any;
